import logging
from PySide6 import QtCore
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BaseComponent(QtCore.QObject):
    """Classe base para todos os componentes do sistema."""

    def __init__(self, context: Optional[Any] = None, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)

        self._context: Optional[Any] = None
        self._scene_manager = None
        self._is_loaded = False

        if context is not None:
            self.set_context(context)

    @property
    def scene_manager(self):
        if self._scene_manager is None:
            logger.warning(
                f"Acesso ao scene_manager em {self.__class__.__name__} sem contexto definido."
            )
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, value):
        self._scene_manager = value

    def set_context(self, context: Any) -> None:
        if not hasattr(context, "scene_manager"):
            raise AttributeError(
                f"Falha ao injetar contexto em {self.__class__.__name__}. "
                "O objeto de contexto deve possuir o atributo 'scene_manager'."
            )

        self._context = context
        self._scene_manager = context.scene_manager

    @property
    def context(self):
        return self._context

    def setup_component(self) -> None:
        """Inicializa o componente se ainda não estiver carregado."""
        if self._is_loaded:
            return

        self.setup_ui()
        self._is_loaded = True

    def setup_ui(self) -> None:
        """Deve ser implementado pelas subclasses."""
        raise NotImplementedError(
            f"{self.__class__.__name__} deve implementar setup_ui"
        )

    def get_ui(self) -> Any:
        """Deve ser implementado pelas subclasses."""
        raise NotImplementedError(
            f"{self.__class__.__name__} deve implementar get_ui"
        )

    def dispose(self) -> None:
        """Limpa recursos e marca o componente para deleção."""
        self._is_loaded = False
        self.deleteLater()