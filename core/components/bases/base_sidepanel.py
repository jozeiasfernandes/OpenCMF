# core/components/bases/base_side_panel.py

from PySide6 import QtWidgets, QtCore
from typing import Optional, Any
from core.components.bases.base_component import BaseComponent


class BaseSidePanel(BaseComponent):
    # Usamos o nome da classe ou um atributo para identificar o painel
    side_panel_name: str = "Painel Lateral Genérico"

    def __init__(self, context: Any, parent: Optional[QtWidgets.QWidget] = None):
        # A BaseComponent já injeta o scene_manager automaticamente via context
        super().__init__(context=context, parent=parent)

        # Configuração do Layout que todos herdarão
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)  # Margem um pouco mais confortável para painéis
        self.layout.setSpacing(5)

    def setup_component(self):
        """
        O contrato obriga a implementação do setup da UI.
        O Loader chamará este método após instanciar.
        """
        self.setup_ui()
        self._is_loaded = True

    def setup_ui(self) -> None:
        """
        Método a ser sobrescrito pelos painéis específicos.
        """
        pass

    @property
    def event_bus(self):
        """Acesso dinâmico ao barramento de eventos."""
        return self.scene_manager.events if self.scene_manager else None