# Em core/components/bases/base_toolbar.py
from typing import Optional, Any, Callable
from dataclasses import dataclass
from PySide6 import QtWidgets, QtCore, QtGui


@dataclass
class ToolData:
    name: str
    display_name: str
    icon_path: Optional[str]
    tool_tip: str
    callback: Callable
    is_checkable: bool = True


class BaseToolbar(QtWidgets.QToolBar):
    """Classe base para toolbars sem herança múltipla."""

    def __init__(self, context: Any, title: str, parent: Optional[QtWidgets.QWidget] = None, is_movable: bool = True):
        # ✅ CHAMADA DIRETA ao QToolBar (apenas uma vez)
        QtWidgets.QToolBar.__init__(self, title, parent)

        # Guardar contexto
        self._context = context

        self.setWindowTitle(title)
        self.setObjectName(title.lower().replace(" ", "_"))

        self.setMovable(is_movable)
        self.setFloatable(is_movable)

        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setIconSize(QtCore.QSize(24, 24))

    @property
    def context(self):
        return self._context

    def setup_ui(self):
        """Sobrescreva este método nas subclasses para adicionar ferramentas."""
        pass

    def add_spacer(self):
        """Adiciona um espaçador para organizar grupos."""
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.addWidget(spacer)

    def set_display_mode(self, mode: str):
        """Altera dinamicamente a exibição: 'icon', 'text' ou 'icon_text'."""
        modes = {
            'icon': QtCore.Qt.ToolButtonIconOnly,
            'text': QtCore.Qt.ToolButtonTextOnly,
            'icon_text': QtCore.Qt.ToolButtonTextBesideIcon
        }
        self.setToolButtonStyle(modes.get(mode, QtCore.Qt.ToolButtonIconOnly))

    def add_tool_button(self, tool_data: ToolData, icon: Optional[QtGui.QIcon] = None) -> QtWidgets.QToolButton:
        btn = QtWidgets.QToolButton()
        btn.setText(tool_data.display_name)
        btn.setToolTip(tool_data.tool_tip)
        btn.setCheckable(tool_data.is_checkable)

        if icon:
            btn.setIcon(icon)

        btn.clicked.connect(tool_data.callback)
        self.addWidget(btn)
        return btn

    def get_ui(self) -> QtWidgets.QToolBar:
        return self