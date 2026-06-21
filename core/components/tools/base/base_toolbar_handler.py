from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

if TYPE_CHECKING:
    from core.components.tools.base.base_tool import BaseTool, InteractionContext


class BaseToolbarHandler(QtCore.QObject):
    def __init__(self, toolbar: QtWidgets.QToolBar, context: Optional[InteractionContext] = None):
        super().__init__()
        self.toolbar = toolbar
        self.context = context
        self.action_group = QtGui.QActionGroup(self)
        self.action_group.setExclusive(True)

    @property
    def components_path(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    def load_tools(self, tools: List[BaseTool]):
        for tool in tools:
            self.register_tool(tool)

    def register_tool(self, tool: BaseTool):
        action = QtGui.QAction(tool.get_qicon(), tool.display_name, self.toolbar)
        action.setCheckable(True)
        action.setToolTip(tool.tool_tip)
        action.triggered.connect(lambda checked, t=tool: self._handle_toggle(t, checked))
        self.action_group.addAction(action)
        self.toolbar.addAction(action)

    def _handle_toggle(self, tool: BaseTool, checked: bool):
        if checked:
            if self.context:
                tool.activate(self.context)
        else:
            tool.deactivate()

    def clear_toolbar(self):
        self.toolbar.clear()
        for action in self.action_group.actions():
            self.action_group.removeAction(action)