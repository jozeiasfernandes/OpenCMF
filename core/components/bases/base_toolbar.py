from PySide6 import QtWidgets, QtCore, QtGui
from abc import abstractmethod
from typing import Optional, Any


class BaseToolbar(QtWidgets.QToolBar):
    def __init__(self, title: str, modulo: Any = None, scene_manager: Any = None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(title, parent)
        self.modulo = modulo
        self.scene_manager = scene_manager
        self.setWindowTitle(title)
        self.setObjectName(title.lower().replace(" ", "_"))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setIconSize(QtCore.QSize(24, 24))
        self.setup_ui()

    @abstractmethod
    def setup_ui(self):
        pass

    def add_tool_button(self, text: str, callback, icon: Optional[QtGui.QIcon] = None, tooltip: str = ""):
        btn = QtWidgets.QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        if icon:
            btn.setIcon(icon)
        btn.clicked.connect(callback)
        self.addWidget(btn)
        return btn

    @property
    def has_scene(self) -> bool:
        return self.scene_manager is not None