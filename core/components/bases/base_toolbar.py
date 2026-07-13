from PySide6 import QtWidgets, QtCore, QtGui
from typing import Optional, Any
from core.components.bases.base_component import BaseComponent


class BaseToolbar(BaseComponent, QtWidgets.QToolBar):
    def __init__(self, context: Any, title: str, parent: Optional[QtWidgets.QWidget] = None):
        # Inicializa o BaseComponent (para gerenciar SceneManager, etc.)
        # e o QToolBar (UI)
        BaseComponent.__init__(self, context=context, parent=parent)
        QtWidgets.QToolBar.__init__(self, title, parent)

        self.setWindowTitle(title)
        self.setObjectName(title.lower().replace(" ", "_"))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setIconSize(QtCore.QSize(24, 24))

    def setup_component(self):
        """
        O Loader chamará este método após instanciar.
        É aqui que o setup_ui será executado.
        """
        self.setup_ui()
        self._is_loaded = True

    def setup_ui(self):
        """Método a ser implementado pelas Toolbars específicas."""
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

    def get_ui(self):
        return self