import logging
from typing import Optional, Any, Dict
from PySide6 import QtCore
from core.components.bases.base_tool.base_tool import BaseTool, InteractionContext

logger = logging.getLogger(__name__)


class ToolManager(QtCore.QObject):
    tool_changed = QtCore.Signal(object)

    def __init__(self, event_bus: Optional[Any] = None, context: Optional[InteractionContext] = None):
        super().__init__()
        self._event_bus = event_bus
        self._context = context
        self.active_tool: Optional[BaseTool] = None
        self._tools: Dict[str, BaseTool] = {}  # Armazena as ferramentas registradas

        # Se houver um event_bus disponível, inscrevemos nos eventos de interação do visualizador
        if self._event_bus:
            self._setup_event_subscriptions()

    def _setup_event_subscriptions(self) -> None:
        """Inscreve o ToolManager nos eventos globais de interação das janelas centrais."""
        # Exemplo de eventos emitidos pelas views centrais
        self._event_bus.subscribe("VIEWER_MOUSE_PRESS", self._on_viewer_mouse_press)
        self._event_bus.subscribe("VIEWER_MOUSE_MOVE", self._on_viewer_mouse_move)
        self._event_bus.subscribe("VIEWER_MOUSE_RELEASE", self._on_viewer_mouse_release)
        self._event_bus.subscribe("VIEWER_WHEEL", self._on_viewer_wheel)
        self._event_bus.subscribe("VIEWER_KEY_PRESS", self._on_viewer_key_press)
        self._event_bus.subscribe("VIEWER_KEY_RELEASE", self._on_viewer_key_release)

    def register_tool(self, key: str, tool: BaseTool) -> None:
        """Registra uma ferramenta no gerenciador."""
        self._tools[key] = tool

    def get_tool(self, key: str) -> Optional[BaseTool]:
        """Retorna uma ferramenta com base na chave solicitada pela Toolbar."""
        return self._tools.get(key, None)

    def set_context(self, context: InteractionContext) -> None:
        """Define o contexto caso não esteja disponível na inicialização."""
        self._context = context

    def set_event_bus(self, event_bus: Any) -> None:
        """Define ou altera o barramento de eventos."""
        self._event_bus = event_bus
        self._setup_event_subscriptions()

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

    # Handlers disparados pelo EventBus (recebidos das janelas centrais)
    def _on_viewer_mouse_press(self, x: int, y: int, button: str, modifiers: Any = None, **kwargs) -> bool:
        return self.mouse_press(x, y, button, modifiers)

    def _on_viewer_mouse_move(self, x: int, y: int, modifiers: Any = None, **kwargs) -> bool:
        return self.mouse_move(x, y, modifiers)

    def _on_viewer_mouse_release(self, x: int, y: int, button: str, modifiers: Any = None, **kwargs) -> bool:
        return self.mouse_release(x, y, button, modifiers)

    def _on_viewer_wheel(self, x: int, y: int, delta: int, modifiers: Any = None, **kwargs) -> bool:
        if delta > 0:
            return self.wheel_forward(x, y, modifiers)
        else:
            return self.wheel_backward(x, y, modifiers)

    def _on_viewer_key_press(self, key: str, modifiers: Any = None, **kwargs) -> bool:
        return self.key_press(key, modifiers)

    def _on_viewer_key_release(self, key: str, modifiers: Any = None, **kwargs) -> bool:
        return self.key_release(key, modifiers)

    # Métodos delegados de forma limpa
    def mouse_press(self, x: int, y: int, button: str, modifiers: Any = None) -> bool:
        return self._delegate_event("mouse_press", x, y, button, modifiers)

    def mouse_move(self, x: int, y: int, modifiers: Any = None) -> bool:
        return self._delegate_event("mouse_move", x, y, modifiers)

    def mouse_release(self, x: int, y: int, button: str, modifiers: Any = None) -> bool:
        return self._delegate_event("mouse_release", x, y, button, modifiers)

    def wheel_forward(self, x: int, y: int, modifiers: Any = None) -> bool:
        return self._delegate_event("wheel_forward", x, y, modifiers)

    def wheel_backward(self, x: int, y: int, modifiers: Any = None) -> bool:
        return self._delegate_event("wheel_backward", x, y, modifiers)

    def key_press(self, key: str, modifiers: Any = None) -> bool:
        return self._delegate_event("key_press", key, modifiers)

    def key_release(self, key: str, modifiers: Any = None) -> bool:
        return self._delegate_event("key_release", key, modifiers)