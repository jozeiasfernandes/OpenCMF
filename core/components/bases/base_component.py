from PySide6 import QtCore
from typing import Any, Optional

class BaseComponent(QtCore.QObject):
    """
    Classe base para todos os componentes do sistema.
    Refatorada para permitir injeção de contexto flexível e evitar
    conflitos em hierarquias de herança múltipla.
    """

    def __init__(self, context: Optional[Any] = None, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)
        self._context = context
        # Usar atributo privado para evitar conflitos com propriedades
        self._scene_manager = getattr(context, "scene_manager", None) if context else None
        self._is_loaded = False

    @property
    def scene_manager(self):
        """Retorna o scene_manager do contexto."""
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, value):
        """Permite definir o scene_manager."""
        self._scene_manager = value

    def set_context(self, context: Any):
        """
        Permite injetar o contexto após a inicialização do widget.
        Útil para evitar erros de herança múltipla no __init__.
        """
        self._context = context
        self._scene_manager = getattr(context, "scene_manager", None)

    @property
    def context(self):
        return self._context

    def setup_component(self):
        """Ciclo de vida para inicialização."""
        if self._is_loaded:
            return
        self.setup_ui()
        self._is_loaded = True

    def setup_ui(self):
        raise NotImplementedError(f"{self.__class__.__name__} deve implementar setup_ui")

    def get_ui(self) -> Any:
        raise NotImplementedError(f"{self.__class__.__name__} deve implementar get_ui")

    def dispose(self):
        self._is_loaded = False
        self.deleteLater()