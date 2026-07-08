import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any

from PySide6 import QtWidgets, QtCore
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.scene_manager import SceneManager
from core.scene.events.scene_events import OBJECT_ADDED
from core.scene.events.event_bus import EventBus
from core.scene.selection import selection_manager
from core.scene.utils.scene_utils import SceneUtils
from modules.base_module.base_module import ModuloBase
from core.volume.segmentation_engine import SegmentacaoEngine
from core.components.toolboxes.segmentation_toolbox import SegmentacaoWidget


class Modulo(ModuloBase):
    def __init__(self, scene_manager: Optional[Any] = None):
        # A chamada super() deve respeitar a assinatura de ModuloBase
        super().__init__(scene_manager=scene_manager)

        self.nome = "Segmentação"
        self.id = "modulo.segmentacao"

        self.engine_seg = SegmentacaoEngine()
        self.widget_seg = SegmentacaoWidget()

        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_seg.solicitarMascara.connect(self._executar_threshold)
        self.widget_seg.solicitarExportarSTL.connect(self._executar_exportacao_stl)

    def inicializar(self, caminho_paciente: str) -> None:
        # Chama a inicialização base que define self.pasta_paciente
        super().inicializar(caminho_paciente)
        # Lógica específica de inicialização do seu módulo aqui

    def _executar_threshold(self):
        if not self.scene_manager:
            return

        polydata = self.engine_seg.get_polydata()
        novo_obj = SceneUtils.create_mesh_object("Segmentação", polydata)

        self.scene_manager.add_object(novo_obj)
        # Se você estiver usando o EventBus global, certifique-se de que ele
        # está sendo acessado corretamente pelo sistema de renderização
        EventBus.emit(OBJECT_ADDED, {"object": novo_obj})

    def _executar_exportacao_stl(self):
        pass

    def get_workspace(self) -> QtWidgets.QWidget:

        # Verifica se o gerenciador existe E se ele possui uma view válida
        if self.scene_manager is not None and hasattr(self.scene_manager, 'view'):
            view = self.scene_manager.view
            # Garantia extra: verifica se a view não foi descartada
            if view is not None:
                return view

        # Fallback para o método base ou um widget vazio
        return super().get_workspace()

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Ferramentas": self.widget_seg
        }

if __name__ == "__main__":
    from PySide6 import QtWidgets
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    import vtkmodules.all as vtk

    # Imports necessários para a ponte de renderização
    from core.scene.rendering.scene_bridge import SceneBridge
    from core.scene.rendering.vtk_scene_renderer import VTKSceneRenderer
    from core.scene.rendering.vtk_actor_factory import VTKActorFactory
    from core.scene.scene_state import SceneState
    from core.scene.selection.selection_manager import SelectionManager

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # 1. Dependências Core
    event_bus = EventBus()
    state = SceneState()
    object_registry = ObjectRegistry()
    actor_registry = ActorRegistry()


    # 2. Inicialização do Manager
    scene_manager = SceneManager(
        state=state, event_bus=event_bus,
        object_registry=object_registry, actor_registry=actor_registry,
        selection_manager=selection_manager
    )

    # 3. Configuração da Ponte de Renderização (O "Elo Perdido")
    vtk_widget = QVTKRenderWindowInteractor()
    renderer = vtk.vtkRenderer()
    vtk_widget.GetRenderWindow().AddRenderer(renderer)
    vtk_widget.Initialize()

    # Inicializa os componentes de renderização do OpenCMF
    vtk_renderer = VTKSceneRenderer(renderer)
    factory = VTKActorFactory(vtk_module=vtk)

    # A ponte conecta o SceneManager (Model) ao VTK (View)
    bridge = SceneBridge(
        event_bus=event_bus,
        object_registry=object_registry,
        actor_registry=actor_registry,
        renderer=vtk_renderer,
        factory=factory
    )

    # 4. Inicialização do Módulo
    modulo = Modulo(scene_manager=scene_manager)
    path_teste = Path(os.path.expanduser("~")) / "OpenCMF_Debug"
    path_teste.mkdir(parents=True, exist_ok=True)
    modulo.inicializar(str(path_teste))

    # 5. UI
    win = QtWidgets.QMainWindow()
    win.setWindowTitle("OpenCMF - Teste de Módulo de Segmentação")
    win.setCentralWidget(vtk_widget)

    dock = QtWidgets.QDockWidget("Ferramentas")
    tabs = QtWidgets.QTabWidget()
    for n, w in modulo.get_toolboxes().items():
        tabs.addTab(w, n)
    dock.setWidget(tabs)

    win.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    win.resize(1200, 800)
    win.show()

    # Render inicial
    renderer.ResetCamera()

    sys.exit(app.exec())