from typing import Optional, Dict
from PySide6 import QtWidgets, QtCore

# Workspace
from core.workspace.models.contracts import IModule

# Settings
from settings.logs.archives.module_log import Module_Logger

class ModuleBase(QtWidgets.QWidget):
    """Base class for OpenCMF workspace modules."""

    id: str = "undefined.id"
    name: str = "Generic Module"

    completed = QtCore.Signal()

    def __init__(
            self,
            context,
            parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        self.context = context

        if isinstance(context, dict):
            self.event_bus = context.get("event_bus")
        else:
            self.event_bus = getattr(context, "event_bus", None)

        self.module_logger = Module_Logger(
            modulo_instance=self
        )

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

    # ---------------------------------------------------------
    # Workspace interface
    # ---------------------------------------------------------

    def get_toolbar(
        self,
    ) -> Optional[QtWidgets.QToolBar]:
        return None

    def get_central_area(self) -> QtWidgets.QWidget:
        return self

    def get_side_panel(
        self,
    ) -> Dict[str, QtWidgets.QWidget]:
        return {}

    def get_bottom_panel(
        self,
    ) -> Optional[QtWidgets.QWidget]:
        return None

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def initialize(
        self,
        patient_path: str,
    ) -> None:
        self.configure_resources(patient_path)
        self.module_logger.log_full_state()

    def configure_resources(
        self,
        patient_path: str,
    ) -> None:
        pass

    def check_prerequisites(self) -> tuple[bool, str]:
        return True, ""

    def validate_transition(self) -> bool:
        return True

    def cleanup(self) -> None:
        pass