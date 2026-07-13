# core/components/side_panel_container/side_panel_manager.py

from PySide6 import QtWidgets, QtCore
from .side_panel_container import SidePanelContainer


class SidePanelManager(QtCore.QObject):
    """
    Gerencia o estado dos painéis laterais (docking, visibilidade,
    injeção via Registry).
    """

    def __init__(self, parent_window: QtWidgets.QMainWindow):
        super().__init__()
        self.parent_window = parent_window
        self.container = SidePanelContainer("Inspector")

        # Define o comportamento padrão de docking
        self.parent_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.container)

    def set_position(self, area: QtCore.Qt.DockWidgetArea):
        """Alterna a posição do painel (ex: Left vs Right)."""
        self.parent_window.removeDockWidget(self.container)
        self.parent_window.addDockWidget(area, self.container)

    def toggle_floating(self):
        """Alterna o estado de floating do dock."""
        self.container.setFloating(not self.container.isFloating())