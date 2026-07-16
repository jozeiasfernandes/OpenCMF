from PySide6 import QtWidgets, QtCore
from .side_panel_container import SidePanelContainer


class SidePanelManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.container = SidePanelContainer("Side Panel")

        self.container.setMinimumWidth(200)

    def set_position(self, area: QtCore.Qt.DockWidgetArea):
        print("A posição deve ser alterada via layout do WorkspaceManager.")

    def toggle_floating(self):
        """Alterna o estado de floating (se o container suportar)."""
        if hasattr(self.container, "setFloating"):
            self.container.setFloating(not self.container.isFloating())

    def clear_all(self):
        """Limpa o conteúdo do painel lateral."""
        content_widget = self.container.widget() if hasattr(self.container, "widget") else self.container

        layout = content_widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def add_panel(self, name, widget):
        """Método auxiliar para injetar widgets no container."""
        # Verifique se o seu SidePanelContainer possui um método de adição
        if hasattr(self.container, "add_panel"):
            self.container.add_panel(name, widget)