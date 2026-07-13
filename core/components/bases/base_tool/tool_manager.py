import logging
from typing import Optional, Any
from PySide6 import QtCore
from core.components.bases.base_tool.base_tool import BaseTool, InteractionContext

logger = logging.getLogger(__name__)


class ToolManager(QtCore.QObject):
    tool_changed = QtCore.Signal(object)

    def __init__(self, context: Optional[InteractionContext] = None):
        super().__init__()
        self._context = context
        self.active_tool: Optional[BaseTool] = None

    def set_context(self, context: InteractionContext) -> None:
        """Define o contexto caso não esteja disponível na inicialização."""
        self._context = context

    def activate_tool(self, tool: Optional[BaseTool]) -> None:
        if self.active_tool == tool:
            return

        # 1. Limpeza segura
        self.deactivate_all()

        # 2. Ativação
        self.active_tool = tool
        if self.active_tool and self._context:
            try:
                self.active_tool.activate(self._context)
            except Exception as e:
                logger.error(f"Erro ao ativar {self.active_tool}: {e}")
                self.active_tool = None

        self.tool_changed.emit(self.active_tool)

    def deactivate_all(self) -> None:
        if self.active_tool:
            try:
                self.active_tool.deactivate()
            except Exception as e:
                logger.error(f"Erro ao desativar {self.active_tool}: {e}")
            finally:
                self.active_tool = None
                self.tool_changed.emit(None)

    def _delegate_event(self, method_name: str, *args, **kwargs) -> bool:
        """Centraliza a execução e tratamento de erros de todos os eventos."""
        if not self.active_tool:
            return False

        method = getattr(self.active_tool, method_name, None)
        if method:
            try:
                return method(*args, **kwargs)
            except Exception as e:
                logger.error(f"Erro na ferramenta {self.active_tool.__class__.__name__} no método {method_name}: {e}")
        return False

    # Métodos delegados de forma limpa
    def mouse_press(self, x: int, y: int, button: str, modifiers: Any = None) -> bool:
        return self._delegate_event("mouse_press", x, y, button, modifiers)

    def mouse_move(self, x: int, y: int, modifiers: Any = None) -> bool:
        return self._delegate_event("mouse_move", x, y, modifiers)

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