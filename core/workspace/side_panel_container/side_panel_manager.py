# core/workspace/side_panel_container/side_panel_manager.py

from PySide6 import QtWidgets, QtCore
from .side_panel_container import SidePanelContainer


class SidePanelManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.container = SidePanelContainer("Side Panel", parent_window)

        # Configurar visibilidade
        self.container.setVisible(True)
        self.container.setMinimumWidth(250)

    def add_panel(self, name: str, widget: QtWidgets.QWidget):
        """Adiciona um widget ao container lateral."""
        if hasattr(self.container, "add_panel"):
            self.container.add_panel(name, widget)
            # Garantir visibilidade
            self.container.setVisible(True)
            widget.setVisible(True)

    def remove_panel(self, name: str):
        """Remove um widget do container lateral."""
        if hasattr(self.container, "remove_panel"):
            self.container.remove_panel(name)

    def clear_all(self):
        """Limpa todos os painéis."""
        if hasattr(self.container, "clear_all"):
            self.container.clear_all()