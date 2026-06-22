from __future__ import annotations
from typing import Optional, Any
from PySide6 import QtCore
from core.components.tools.base.base_tool import BaseTool, InteractionContext

class ToolManager(QtCore.QObject):
    def __init__(self, context: InteractionContext):
        super().__init__()
        self.context = context
        self.active_tool: Optional[BaseTool] = None

    def activate_tool(self, tool: BaseTool) -> None:
        if self.active_tool == tool:
            return

        if self.active_tool:
            self.active_tool.deactivate()

        self.active_tool = tool
        self.active_tool.activate(self.context)

    def deactivate_all(self) -> None:
        if self.active_tool:
            self.active_tool.deactivate()
            self.active_tool = None

    def mouse_press(self, x: int, y: int, button: str, modifiers: Any = None) -> bool:
        if self.active_tool:
            return self.active_tool.mouse_press(x, y, button, modifiers)
        return False

    def mouse_release(self, x: int, y: int, button: str, modifiers: Any = None) -> bool:
        if self.active_tool:
            return self.active_tool.mouse_release(x, y, button, modifiers)
        return False

    def mouse_move(self, x: int, y: int, modifiers: Any = None) -> bool:
        if self.active_tool:
            return self.active_tool.mouse_move(x, y, modifiers)
        return False

    def wheel_forward(self, x: int, y: int, modifiers: Any = None) -> bool:
        if self.active_tool:
            return self.active_tool.wheel_forward(x, y, modifiers)
        return False

    def wheel_backward(self, x: int, y: int, modifiers: Any = None) -> bool:
        if self.active_tool:
            return self.active_tool.wheel_backward(x, y, modifiers)
        return False

    def key_press(self, key: str, modifiers: Any = None) -> bool:
        if self.active_tool:
            return self.active_tool.key_press(key, modifiers)
        return False

    def key_release(self, key: str, modifiers: Any = None) -> bool:
        if self.active_tool:
            return self.active_tool.key_release(key, modifiers)
        return False