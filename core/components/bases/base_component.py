from PySide6 import QtCore
from typing import Any, Optional


class BaseComponent(QtCore.QObject):
    """
    Classe base para todos os componentes do sistema.
    Define o contrato de ciclo de vida para o ComponentLoader.
    """

    def __init__(self, context: Any, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)
        self.context = context
        # Usar o contexto para buscar serviços de forma segura
        self.scene_manager = getattr(context, "scene_manager", None)
        self._is_loaded = False

    def setup_component(self):
        """
        Método de ciclo de vida para inicialização.
        Subclasses devem implementar a lógica de UI aqui.
        """
        if self._is_loaded:
            return

        self.setup_ui()
        self._is_loaded = True

    def setup_ui(self):
        """
        Método interno para ser sobrescrito pelas subclasses.
        Evita a necessidade de sobrescrever o setup_component original.
        """
        raise NotImplementedError(f"{self.__class__.__name__} deve implementar setup_ui")

    def get_ui(self) -> Any:
        """
        Retorna o widget principal do componente.
        Nota: Em classes que herdam de QWidget, retorne 'self'.
        """
        raise NotImplementedError(f"{self.__class__.__name__} deve implementar get_ui")

    def dispose(self):
        """Limpeza de recursos."""
        self._is_loaded = False
        self.deleteLater()