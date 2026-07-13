# core/components/bases/base_component.py

from PySide6 import QtCore
from typing import Any, Optional


class BaseComponent(QtCore.QObject):
    """
    Classe base para todos os componentes do sistema.
    Define o contrato de ciclo de vida para o ComponentLoader.
    """

    def __init__(self, context: Any, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)
        self.context = context  # Referência à App/MainWindow
        self.scene_manager = getattr(context, "scene_manager", None)
        self._is_loaded = False

    def setup_component(self):
        """
        Método chamado pelo Loader após a instanciação.
        Aqui o componente deve configurar sua UI e sinais.
        """
        raise NotImplementedError("Componentes devem implementar setup_component")

    def get_ui(self) -> Any:
        """Retorna o widget principal do componente."""
        raise NotImplementedError("Componentes devem retornar um widget")

    def dispose(self):
        """Método de limpeza para evitar memory leaks."""
        self.deleteLater()