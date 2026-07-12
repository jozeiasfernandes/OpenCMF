from PySide6 import QtWidgets, QtGui, QtCore
from pathlib import Path
from typing import Optional, Any


class BaseContextMenu(QtWidgets.QMenu):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, scene_manager: Any = None):
        super().__init__(parent)
        self.scene_manager = scene_manager
        self.context_object_id: Optional[str] = None
        self.setup_menu()

    def setup_menu(self) -> None:
        pass

    def create_action(
            self,
            text: str,
            callback,
            icon_path: Optional[Path] = None,
            shortcut: Optional[str] = None
    ) -> QtGui.QAction:
        action = QtGui.QAction(text, self)
        if icon_path and icon_path.exists():
            action.setIcon(QtGui.QIcon(str(icon_path)))
        if shortcut:
            action.setShortcut(QtGui.QKeySequence(shortcut))
            action.setShortcutVisibleInContextMenu(True)
        action.triggered.connect(callback)
        self.addAction(action)
        return action

    def show_at_cursor(self, object_id: Optional[str] = None):
        self.context_object_id = object_id
        self.exec(QtGui.QCursor.pos())

    @property
    def has_scene(self) -> bool:
        return self.scene_manager is not None