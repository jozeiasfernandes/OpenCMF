import logging
from typing import Any, Optional, Dict, Protocol, Set
from PySide6 import QtCore

logger = logging.getLogger(__name__)


class SceneManagerProtocol(Protocol):
    """Protocolo para SceneManager."""

    def load_scene(self, scene_id: str) -> None: ...

    def get_current_scene(self) -> Any: ...


class ToolManagerProtocol(Protocol):
    """Protocolo para ToolManager."""

    def activate_tool(self, tool_id: str) -> None: ...

    def get_active_tool(self) -> Any: ...


class EventBusProtocol(Protocol):
    """Protocolo para EventBus."""

    def publish(self, event: str, data: Any) -> None: ...

    def subscribe(self, event: str, callback) -> None: ...


class AppContext:
    """Contexto centralizado da aplicação."""

    def __init__(
            self,
            scene_manager: Optional[SceneManagerProtocol] = None,
            tool_manager: Optional[ToolManagerProtocol] = None,
            event_bus: Optional[EventBusProtocol] = None,
            settings: Optional[Dict[str, Any]] = None,
            user_data: Optional[Dict[str, Any]] = None
    ):
        self.scene_manager = scene_manager
        self.tool_manager = tool_manager
        self.event_bus = event_bus
        self.settings = settings or {}
        self.user_data = user_data or {}


class BaseComponent(QtCore.QObject):
    """Classe base para componentes com contexto (herda apenas de QObject para evitar conflito de metaclasse com o Qt)."""

    REQUIRED_ATTRS: Set[str] = {"scene_manager", "tool_manager", "event_bus"}

    def __init__(self, context: Optional[Any] = None, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)
        self._context: Optional[Any] = None
        self._loaded: bool = False
        self._disposed: bool = False

        if context is not None:
            self.set_context(context)

    def _resolve_context(self, context: Any) -> Any:
        """Resolve contexto real a partir de wrappers."""
        if hasattr(context, "app_context") and context.app_context is not None:
            return context.app_context
        return context

    @property
    def target_context(self) -> Optional[Any]:
        """Contexto interno resolvido."""
        if self._context is None:
            return None
        return self._resolve_context(self._context)

    def _safe_get_attr(self, attr_name: str) -> Optional[Any]:
        """Obtém atributo do contexto com validação."""
        self._ensure_not_disposed()
        ctx = self.target_context
        if ctx is not None and hasattr(ctx, attr_name):
            return getattr(ctx, attr_name)

        logger.warning(
            f"'{attr_name}' indisponível em {self.__class__.__name__} "
            f"(contexto: {ctx is not None})"
        )
        return None

    def _ensure_not_disposed(self) -> None:
        """Verifica se componente foi descartado."""
        if self._disposed:
            raise RuntimeError(f"{self.__class__.__name__} já foi descartado")

    @property
    def scene_manager(self) -> Optional[SceneManagerProtocol]:
        return self._safe_get_attr("scene_manager")

    @scene_manager.setter
    def scene_manager(self, value: SceneManagerProtocol) -> None:
        ctx = self.target_context
        if ctx is not None and hasattr(ctx, "scene_manager"):
            ctx.scene_manager = value

    @property
    def tool_manager(self) -> Optional[ToolManagerProtocol]:
        return self._safe_get_attr("tool_manager")

    @property
    def event_bus(self) -> Optional[EventBusProtocol]:
        return self._safe_get_attr("event_bus")

    def set_context(self, context: Any) -> None:
        """Define contexto com validação completa."""
        self._ensure_not_disposed()
        target_context = self._resolve_context(context)

        missing = [attr for attr in self.REQUIRED_ATTRS if not hasattr(target_context, attr)]
        if missing:
            raise AttributeError(
                f"Contexto inválido para {self.__class__.__name__}. "
                f"Faltando: {', '.join(missing)}"
            )

        self._context = context

    @property
    def context(self) -> Optional[Any]:
        return self._context

    def setup_component(self) -> None:
        """Inicializa componente se não carregado."""
        self._ensure_not_disposed()
        if self._loaded:
            return

        self.setup_ui()
        self._loaded = True

    def setup_ui(self) -> None:
        """Configura interface do componente."""
        raise NotImplementedError(f"{self.__class__.__name__} deve implementar setup_ui")

    def get_ui(self) -> Any:
        """Retorna interface do componente."""
        raise NotImplementedError(f"{self.__class__.__name__} deve implementar get_ui")

    def dispose(self) -> None:
        """Libera recursos do componente."""
        if self._disposed:
            return

        self._loaded = False
        self._disposed = True
        self.deleteLater()