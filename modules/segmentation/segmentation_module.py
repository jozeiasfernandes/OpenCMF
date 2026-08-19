from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from PySide6 import QtWidgets

# Scene
from application.scene.events.scene_events import SceneEvents
from application.scene.utils.factory import SceneObjectFactory

# Components
from core.components.side_panel.segmentation_sidepanel import Segmentation_SidePanel
from core.components.central_area.viewer_3d_dicom_central_area import Viewer3D_Dicom_Widget_CentralArea

# Workspace
from core.workspace.modules.base.base_module import ModuleBase

# Volume
from domain.volume.segmentation.engines.segmentation_engine import ThresholdSegmentationEngine

# Logs
logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Module(ModuleBase):

    def __init__(
            self,
            context: Any,
            parent: Optional[QtWidgets.QWidget] = None,
            **kwargs: Any,
    ) -> None:
        super().__init__(context=context, parent=parent)

        self.nome = "segmentation"
        self.id = "modulo.segmentacao"

        self.scene_manager = kwargs.get("scene_manager") or getattr(context, "scene_manager", None)
        self.event_bus = kwargs.get("event_bus") or getattr(context, "event_bus", None)

        viewer_registry = kwargs.get("viewer_registry") or getattr(context, "viewer_registry", None)
        if viewer_registry is None:
            class DummyRegistry:
                def register(self, *args, **kwargs): pass

            self.viewer_registry = DummyRegistry()
        else:
            self.viewer_registry = viewer_registry

        self.engine_seg = ThresholdSegmentationEngine()

        self.widget_seg = Segmentation_SidePanel(context=context)

        self.widget_central = Viewer3D_Dicom_Widget_CentralArea(
            context=context,
            title="Visualizador 3D",
            cor="#2c3e50",
            event_bus=self.event_bus,
            viewer_registry=self.viewer_registry
        )

        self.widget_central.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.widget_central.setMinimumSize(400, 300)

        self.viewer = self.widget_central

        self._connect_signals()

    # =========================================================================
    # PUBLIC METHODS (LIFECYCLE & GETTERS)
    # =========================================================================
    def initialize(self, path_pacient: str) -> None:
        """Inicializa o módulo com o path do paciente."""
        super().initialize(path_pacient)
        logger.info(f"Módulo '{self.nome}' inicializado com paciente: {path_pacient}")

    def cleanup(self) -> None:
        """Limpeza segura de widgets evitando erros de C++/Shiboken."""
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
        self.viewer = None
        super().cleanup()
        logger.info(f"Módulo '{self.nome}' limpo com sucesso.")

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna os painéis laterais (side_panels) do módulo."""
        side_panels = super().get_side_panel()
        side_panels["Ferramentas"] = self.widget_seg
        return side_panels

    # =========================================================================
    # PRIVATE HELPERS & SLOTS (SIGNALS & ACTIONS)
    # =========================================================================
    def _connect_signals(self) -> None:
        if hasattr(self.widget_seg, 'requestMask'):
            self.widget_seg.requestMask.connect(self._execute_threshold)

    def _execute_threshold(self) -> None:
        if not self.scene_manager:
            logger.warning("Scene manager não disponível para executar o threshold.")
            return
        polydata = self.engine_seg.get_polydata()
        novo_obj = SceneObjectFactory.create_mesh_object("Segmentação", polydata)
        self.scene_manager.add_object(novo_obj)
        if self.event_bus:
            self.event_bus.emit(SceneEvents.OBJECT_ADDED, {"object": novo_obj})
        else:
            EventBus.emit(SceneEvents.OBJECT_ADDED, {"object": novo_obj})

    def _execute_stl_export(self) -> None:
        pass


if __name__ == "__main__":
    import sys
    from unittest.mock import MagicMock

    # Patient
    from core.settings.paths.list_paths import PATIENTS_DIR

    # Components
    from core.components.bases.base_component import AppContext
    from core.components.bases.base_tool.tool_manager import ToolManager

    # Scene
    from core.application.scene.events.event_bus import EventBus

    # Workspace
    from core.workspace.workspace_manager import WorkspaceManager
    from core.workspace.models.module_factory import ModuleFactory
    from core.workspace.layout.layout import ModuleDistributor

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    contexto_mock = AppContext(
        scene_manager=MagicMock(),
        tool_manager=ToolManager(),
        event_bus=EventBus()
    )

    ModuleFactory.register("modulo.segmentacao", Module)
    ModuleFactory.set_context(contexto_mock)

    window = WorkspaceManager()
    window.setWindowTitle("OpenCMF - Teste do Módulo de Segmentação")
    window.resize(1200, 800)

    modulo_instancia = ModuleFactory.create("modulo.segmentacao")
    if modulo_instancia:
        # Aponta o debug para dentro da estrutura PATIENTS_DIR padronizada
        debug_patient_path = PATIENTS_DIR / "debug_paciente"
        modulo_instancia.initialize(str(debug_patient_path))

        ModuleDistributor.distribute(
            modulo_instancia,
            window.toolbar_manager,
            window.side_manager,
            window.central_manager
        )

    window.show()
    sys.exit(app.exec())