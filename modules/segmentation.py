import sys
import os
from pathlib import Path
from typing import Dict, Optional, Any

from PySide6 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtkmodules.all as vtk

from modules.base_module.base_module import ModuloBase
from core.workspace.contracts import IModule
from core.scene.utils.factory import SceneObjectFactory
from core.scene.events.scene_events import SceneEvents
from core.scene.events.event_bus import EventBus
from core.volume.segmentation_engine import SegmentacaoEngine
from core.components.side_panel.segmentation_sidepanel import SegmentacaoWidget

from core.scene.registry.object_registry import ObjectRegistry
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.scene_manager import SceneManager
from core.scene.io.importer import ObjectImporter
from core.scene.rendering.scene_bridge import SceneBridge
from core.scene.rendering.vtk_scene_renderer import VTKSceneRenderer
from core.scene.rendering.vtk_actor_factory import VTKActorFactory
from core.scene.scene_state import SceneState
from core.scene.selection.selection_manager import SelectionManager as SelectionManagerClass


class Modulo(ModuloBase):
    def __init__(self, scene_manager: Optional[Any] = None):
        super().__init__(scene_manager=scene_manager)
        self.nome = "Segmentação"
        self.id = "modulo.segmentacao"
        self.engine_seg = SegmentacaoEngine()
        self.widget_seg = SegmentacaoWidget()
        self.selection_manager = getattr(self.scene_manager, 'selection_manager', None)
        self._conectar_sinais()

    def _criar_main_widget(self) -> QtWidgets.QWidget:
        if self.scene_manager is not None and hasattr(self.scene_manager, 'view'):
            return self.scene_manager.view
        return QtWidgets.QWidget()

    def _conectar_sinais(self):
        self.widget_seg.solicitarMascara.connect(self._executar_threshold)
        self.widget_seg.solicitarExportarSTL.connect(self._executar_exportacao_stl)

    def get_main_widget(self) -> QtWidgets.QWidget:
        if self.scene_manager is not None and hasattr(self.scene_manager, 'view'):
            return self.scene_manager.view
        return QtWidgets.QWidget()

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Ferramentas": self.widget_seg
        }

    def _executar_threshold(self):
        if not self.scene_manager:
            return
        polydata = self.engine_seg.get_polydata()
        novo_obj = SceneObjectFactory.create_mesh_object("Segmentação", polydata)
        self.scene_manager.add_object(novo_obj)
        EventBus.emit(SceneEvents.OBJECT_ADDED, {"object": novo_obj})

    def _executar_exportacao_stl(self):
        pass

    def cleanup(self) -> None:
        super().cleanup()


IModule.register(Modulo)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # 1. Preparar caminho (necessário para o Importer)
    path_teste = Path(os.path.expanduser("~")) / "OpenCMF_Debug"
    path_teste.mkdir(parents=True, exist_ok=True)

    # 2. Dependências Core
    event_bus = EventBus()
    state = SceneState()
    object_registry = ObjectRegistry()
    actor_registry = ActorRegistry()
    selection_manager = SelectionManagerClass(state=state, event_bus=event_bus)

    # CORREÇÃO: Inicialize o Importer aqui
    importer = ObjectImporter(patient_path=str(path_teste))

    # 3. Inicialização do Manager (Agora com o argumento 'importer')
    scene_manager = SceneManager(
        state=state,
        event_bus=event_bus,
        object_registry=object_registry,
        actor_registry=actor_registry,
        selection_manager=selection_manager,
        importer=importer  # O argumento que estava faltando
    )

    # Configuração da Ponte de Renderização
    vtk_widget = QVTKRenderWindowInteractor()
    renderer = vtk.vtkRenderer()
    vtk_widget.GetRenderWindow().AddRenderer(renderer)
    vtk_widget.Initialize()

    vtk_renderer = VTKSceneRenderer(renderer)
    factory = VTKActorFactory(vtk_module=vtk)
    bridge = SceneBridge(
        event_bus=event_bus,
        object_registry=object_registry,
        actor_registry=actor_registry,
        renderer=vtk_renderer,
        factory=factory
    )

    # Inicialização do Módulo
    modulo = Modulo(scene_manager=scene_manager)

    path_teste = Path(os.path.expanduser("~")) / "OpenCMF_Debug"
    path_teste.mkdir(parents=True, exist_ok=True)
    modulo.inicializar(str(path_teste))

    # UI
    win = QtWidgets.QMainWindow()
    win.setWindowTitle("OpenCMF - Teste de Módulo de Segmentação")
    win.setCentralWidget(modulo.get_main_widget())

    dock = QtWidgets.QDockWidget("Ferramentas")
    tabs = QtWidgets.QTabWidget()
    for n, w in modulo.get_toolboxes().items():
        tabs.addTab(w, n)
    dock.setWidget(tabs)
    win.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    win.resize(1200, 800)
    win.show()

    renderer.ResetCamera()
    sys.exit(app.exec())