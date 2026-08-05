from typing import Optional, Callable, Any, Protocol, TYPE_CHECKING
from dataclasses import dataclass
from PySide6 import QtWidgets, QtCore, QtGui

from core.components.bases.base_component import AppContext

if TYPE_CHECKING:
    from core.components.bases.base_tool.tool_manager import ToolManager
    from core.scene.scene_manager import SceneManager
    from core.components.bases.base_tool.base_tool import BaseTool


@dataclass
class ToolData:
    """Dados para criação de botões de ferramentas na toolbar."""
    name: str
    display_name: str
    icon_path: Optional[str]
    tool_tip: str
    callback: Callable
    is_checkable: bool = True


class BaseToolbar(QtWidgets.QToolBar):
    """
    Classe base para toolbars com injeção de dependência centralizada via AppContext único.
    """

    tool_toggled = QtCore.Signal(object, bool)  # tool, checked

    def __init__(self,
                 title: str,
                 app_context: AppContext,
                 parent: Optional[QtWidgets.QWidget] = None,
                 is_movable: bool = True):

        super().__init__(title, parent)

        # Injeção de dependência centralizada
        self.app = app_context
        self._is_initialized = False
        self._action_group = QtGui.QActionGroup(self)
        self._action_group.setExclusive(True)

        self.setWindowTitle(title)
        self.setObjectName(title.lower().replace(" ", "_"))
        self.setMovable(is_movable)
        self.setFloatable(is_movable)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setIconSize(QtCore.QSize(24, 24))

        self.initialize()

    @property
    def tool_manager(self) -> Optional[Any]:
        return self.app.tool_manager if hasattr(self.app, "tool_manager") else None

    @property
    def scene_manager(self) -> Optional[Any]:
        return self.app.scene_manager if hasattr(self.app, "scene_manager") else None

    @property
    def event_bus(self) -> Optional[Any]:
        return self.app.event_bus if hasattr(self.app, "event_bus") else None

    @property
    def settings(self) -> Any:
        return self.app.settings if hasattr(self.app, "settings") else {}

    def initialize(self) -> None:
        if not self._is_initialized:
            self.setup_ui()
            self._is_initialized = True

    def setup_ui(self) -> None:
        pass

    def dispose(self) -> None:
        self.clear()
        self._is_initialized = False
        self._action_group = QtGui.QActionGroup(self)
        self._action_group.setExclusive(True)

    def register_tool(self, tool: 'BaseTool') -> QtGui.QAction:
        action = QtGui.QAction(tool.get_qicon(), tool.display_name, self)
        action.setCheckable(True)
        action.setToolTip(tool.tool_tip)
        action.setData(tool.name)
        action.triggered.connect(
            lambda checked, t=tool: self._handle_tool_toggle(t, checked)
        )
        self._action_group.addAction(action)
        self.addAction(action)
        return action

    def _handle_tool_toggle(self, tool: 'BaseTool', checked: bool) -> None:
        if self.tool_manager:
            if checked:
                self.tool_manager.activate_tool(tool)
            else:
                if self.tool_manager.active_tool == tool:
                    self.tool_manager.deactivate_all()
        self.tool_toggled.emit(tool, checked)

    def add_spacer(self) -> None:
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.addWidget(spacer)

    def add_action_button(self,
                          text: str,
                          callback: Callable,
                          icon: Optional[QtGui.QIcon] = None,
                          tooltip: str = "",
                          shortcut: Optional[str] = None) -> QtGui.QAction:
        action = QtGui.QAction(text, self)
        if icon:
            action.setIcon(icon)
        if tooltip:
            action.setToolTip(tooltip)
        if shortcut:
            action.setShortcut(QtGui.QKeySequence(shortcut))
            action.setShortcutVisibleInContextMenu(True)
        action.triggered.connect(callback)
        self.addAction(action)
        return action

    def add_separator(self) -> None:
        self.addSeparator()

    def clear(self) -> None:
        for action in self._action_group.actions():
            self._action_group.removeAction(action)
        super().clear()