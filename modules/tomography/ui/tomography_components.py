from __future__ import annotations
import logging
from typing import Dict, Optional, Any
from PySide6 import QtWidgets

# Components
from core.components.toolbars.tomography_toolbar_2 import TomographyToolbar
from domain.volume.visualization.volume_viewer.volume_viewer_widget import VolumeViewerWidget

# Logs
logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")

class TomographyComponents:
    """Responsável por instanciar, gerenciar e prover os componentes visuais da Tomografia."""

    def __init__(self, context: Any, controller: Any):
        self.context = context
        self.controller = controller
        self.viewer: Optional[VolumeViewerWidget] = None
        self.toolbar_handler: Optional[TomographyToolbar] = None

    # ==================================================
    # COMPONENTS
    # ==================================================
    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        if self.toolbar_handler is None:
            if tool_manager and self.context:
                setattr(self.context, "tool_manager", tool_manager)

            self.toolbar_handler = TomographyToolbar(app_context=self.context)
            self.toolbar_handler.initialize()
            logger.info("[TomographyComponents] TomographyToolbar inicializada.")
        return self.toolbar_handler

    def get_central_area(self) -> QtWidgets.QWidget:
        if self.viewer is None:
            ctx = getattr(self.context, "app_context", self.context)
            self.viewer = VolumeViewerWidget(
                context=ctx,
                event_bus=getattr(ctx, "event_bus", getattr(self.controller, "event_bus", None)),
                object_registry=getattr(ctx, "object_registry", getattr(self.context, "object_registry", None))
            )
            self.viewer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            logger.info("[TomographyComponents] VolumeViewerWidget instanciado para a área central.")
        return self.viewer

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna os painéis laterais específicos do módulo de tomografia, se houver."""
        return {}

    # ==================================================
    # CLEANUP
    # ==================================================
    def cleanup(self) -> None:
        if self.viewer:
            try:
                if hasattr(self.viewer, "deleteLater"):
                    self.viewer.deleteLater()
            except RuntimeError:
                pass
            self.viewer = None
        self.toolbar_handler = None
        logger.info("[TomographyComponents] Limpeza de componentes visuais concluída.")