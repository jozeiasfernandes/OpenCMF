from __future__ import annotations
from typing import Optional, Any
from PySide6 import QtCore
from core.components.bases.base_tool.base_tool import BaseTool, InteractionContext

class ToolManager(QtCore.QObject):
    tool_changed = QtCore.Signal(object)

    def __init__(self, context: InteractionContext):
        super().__init__()
        self.context = context
        self.active_tool: Optional[BaseTool] = None

    def activate_tool(self, tool: BaseTool) -> None:
        if self.active_tool == tool:
            return

        if self.active_tool:
            try:
                self.active_tool.deactivate()
            except Exception as e:
                print(f"Erro ao desativar: {e}")

        try:
            tool.activate(self.context)
            self.active_tool = tool
            self.tool_changed.emit(tool)  # Dispara o sinal corretamente
        except Exception as e:
            print(f"Erro ao ativar: {e}")
            self.active_tool = None
            self.tool_changed.emit(None)

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
            try:
                return self.active_tool.mouse_move(x, y, modifiers)
            except Exception as e:
                logger.error(f"Erro na ferramenta {self.active_tool.name}: {e}")
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