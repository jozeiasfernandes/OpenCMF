import logging
from typing import Dict, Optional, Any
from PySide6 import QtWidgets

from core.workspace.contracts import IModule
from core.scene.events.scene_events import SceneEvents
from core.scene.events.event_bus import EventBus
from core.scene.utils.factory import SceneObjectFactory
from core.volume.segmentation_engine import SegmentacaoEngine
from core.components.side_panel.segmentation_sidepanel import Segmentation_SidePanel
from core.components.central_area.viewer_3d_dicom_central_area import Viewer3D_Dicom_Widget_CentralArea

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(IModule):
    def __init__(self, scene_manager: Optional[Any] = None, event_bus: Any = None,
                 viewer_registry: Any = None, **kwargs):
        super().__init__()
        self.nome = "Segmentação"
        self.id = "modulo.segmentacao"

        self.scene_manager = scene_manager
        self.event_bus = event_bus

        if viewer_registry is None:
            class DummyRegistry:
                def register(self, *args, **kwargs): pass

            self.viewer_registry = DummyRegistry()
        else:
            self.viewer_registry = viewer_registry

        self.engine_seg = SegmentacaoEngine()

        self.widget_seg = Segmentation_SidePanel(context=self.scene_manager)

        self.widget_central = Viewer3D_Dicom_Widget_CentralArea(
            context=self.scene_manager,
            title="Visualizador 3D",
            cor="#2c3e50",
            event_bus=self.event_bus,
            viewer_registry=self.viewer_registry
        )

        self.widget_central.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.widget_central.setMinimumSize(400, 300)  # Evita o colapso na inicialização

        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_seg.solicitarMascara.connect(self._executar_threshold)
        self.widget_seg.solicitarExportarSTL.connect(self._executar_exportacao_stl)

    # --- Implementação do IModule ---
    def get_workspace(self) -> QtWidgets.QWidget:
        """O workspace agora busca pelo método get_workspace."""
        return self.widget_central if self.widget_central else QtWidgets.QWidget()

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        return None

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        # O workspace injetará este widget no SidePanelContainer
        return {
            "Ferramentas": self.widget_seg
        }

    def cleanup(self):
        # Limpeza segura de widgets
        for w in [self.widget_seg, self.widget_central]:
            if w:
                try:
                    import shiboken6
                    if shiboken6.isValid(w):
                        w.deleteLater()
                except (RuntimeError, ImportError):
                    pass
        self.widget_seg = None
        self.widget_central = None

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
    from core.workspace.workspace_manager import WorkspaceManager
    from core.workspace.module_factory import ModuleFactory

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    ModuleFactory.register("modulo.segmentacao", Modulo)

    window = WorkspaceManager()
    window.setWindowTitle("OpenCMF - Teste do Módulo de Segmentação")
    window.resize(1200, 800)
    window.show()

    window.header.add_module_tab("modulo.segmentacao", "Segmentação")
    window.on_module_changed("modulo.segmentacao")

    sys.exit(app.exec())