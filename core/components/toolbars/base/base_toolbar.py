from PySide6 import QtWidgets, QtCore
from abc import abstractmethod

class BaseToolbar(QtWidgets.QToolBar):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setWindowTitle(title)
        self.setObjectName(title.lower().replace(" ", "_"))

        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setIconSize(QtCore.QSize(24, 24))

        self.setup_ui()

    @abstractmethod
    def setup_ui(self):
        pass

    def add_tool_button(self, text, callback, icon=None):
        btn = QtWidgets.QPushButton(text)
        if icon:
            btn.setIcon(icon)
        btn.clicked.connect(callback)
        self.addWidget(btn)
        return btn