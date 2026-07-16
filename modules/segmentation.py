import logging
from typing import Dict, Optional, Any
from PySide6 import QtWidgets

from core.workspace.contracts import IModule

from core.scene.events.scene_events import SceneEvents
from core.scene.events.event_bus import EventBus
from core.scene.utils.factory import SceneObjectFactory
from core.volume.segmentation_engine import SegmentacaoEngine
from core.components.side_panel.segmentation_sidepanel import Segmentation_SidePanel

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(IModule):
    def __init__(self, scene_manager: Optional[Any] = None, project_service: Any = None,
                 event_bus: Any = None, **kwargs):
        super().__init__()
        self.nome = "Segmentação"
        self.id = "modulo.segmentacao"

        self.scene_manager = scene_manager
        self.engine_seg = SegmentacaoEngine()

        self.widget_seg = Segmentation_SidePanel(context=self.scene_manager, title="Segmentação")

        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_seg.solicitarMascara.connect(self._executar_threshold)
        self.widget_seg.solicitarExportarSTL.connect(self._executar_exportacao_stl)

    # --- Implementação do IModule ---
    def get_main_widget(self) -> QtWidgets.QWidget:
        # O workspace espera que o módulo forneça o widget central (Viewport)
        if self.scene_manager is not None and hasattr(self.scene_manager, 'view'):
            return self.scene_manager.view
        return QtWidgets.QWidget()

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        # Retorne uma QToolBar aqui se o módulo tiver ferramentas de ação rápida
        return None

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        # O workspace injetará este widget no SidePanelContainer [cite: 6]
        return {
            "Ferramentas": self.widget_seg
        }

    def cleanup(self) -> None:
        """Limpeza necessária para evitar vazamentos de memória no WorkspaceManager[cite: 11]."""
        self.widget_seg.deleteLater()
        self.scene_manager = None
        self.engine_seg = None

    # --- Lógica Interna ---
    def _executar_threshold(self):
        if not self.scene_manager:
            return
        polydata = self.engine_seg.get_polydata()
        novo_obj = SceneObjectFactory.create_mesh_object("Segmentação", polydata)
        self.scene_manager.add_object(novo_obj)
        EventBus.emit(SceneEvents.OBJECT_ADDED, {"object": novo_obj})

    def _executar_exportacao_stl(self):
        pass

if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets
    from core.workspace.workspace_manager import WorkspaceManager
    from core.workspace.module_factory import ModuleFactory

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # 1. Registra o módulo na Factory
    ModuleFactory.register("modulo.segmentacao", Modulo)

    # 2. Inicializa o WorkspaceManager principal
    window = WorkspaceManager()
    window.setWindowTitle("OpenCMF - Teste do Módulo de Segmentação")
    window.resize(1200, 800)
    window.show()

    # 3. Adiciona a aba e força o carregamento inicial do módulo para debug
    window.header.add_module_tab("modulo.segmentacao", "Segmentação")
    window.on_module_changed("modulo.segmentacao")

    sys.exit(app.exec())