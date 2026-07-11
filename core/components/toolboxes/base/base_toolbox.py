from PySide6 import QtWidgets
from typing import Optional, Any
from core.scene.scene_manager import SceneManager
from core.scene.events.event_bus import EventBus


class BaseToolbox(QtWidgets.QWidget):
    toolbox_name: str = "Toolbox Genérica"

    def __init__(
        self,
        scene_manager: Optional[SceneManager] = None,
        parent: Optional[QtWidgets.QWidget] = None
    ):
        super().__init__(parent)
        self.scene_manager = scene_manager
        self.event_bus: Optional[EventBus] = (
            self.scene_manager.events if self.scene_manager else None
        )

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setup_ui()

    def setup_ui(self) -> None:
        pass

    @property
    def has_scene(self) -> bool:
        return self.scene_manager is not None