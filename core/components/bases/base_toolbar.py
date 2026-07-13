from typing import Optional, Any, Callable
from dataclasses import dataclass
from PySide6 import QtWidgets, QtCore, QtGui
from core.components.bases.base_component import BaseComponent


@dataclass
class ToolData:
    name: str
    display_name: str
    icon_path: Optional[str]
    tool_tip: str
    callback: Callable
    is_checkable: bool = True


class BaseToolbar(QtWidgets.QToolBar, BaseComponent):
    def __init__(self, context: Any, title: str, parent: Optional[QtWidgets.QWidget] = None, is_movable: bool = True):
        # A ordem de inicialização garante que o QToolBar receba o pai corretamente
        QtWidgets.QToolBar.__init__(self, title, parent)
        BaseComponent.__init__(self, context=context, parent=parent)

        self.setWindowTitle(title)
        self.setObjectName(title.lower().replace(" ", "_"))

        # Configuração de movimentação (conforme requisito)
        self.setMovable(is_movable)
        self.setFloatable(is_movable)

        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setIconSize(QtCore.QSize(24, 24))

    def setup_ui(self):
        """
        Sobrescreva este método nas subclasses para adicionar ferramentas.
        O BaseComponent.setup_component chamará este método.
        """
        pass

    def add_spacer(self):
        """Adiciona um espaçador para organizar grupos (Esq/Centro/Dir)."""
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