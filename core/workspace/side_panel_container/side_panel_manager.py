# core/workspace/side_panel_container/side_panel_manager.py

from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.loaders.side_panel_manager_loaders.side_panel_manager_loaders import SidePanelManagerLoaders


class SidePanelManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        # Utiliza o gerenciador baseado em abas e QStackedWidget
        self.container = SidePanelManagerLoaders(parent_window)

        # Configurar visibilidade
        self.container.setVisible(True)
        self.container.setMinimumWidth(250)

    def add_panel(self, name: str, widget: QtWidgets.QWidget):
        """Adiciona um widget como uma nova aba no container lateral."""
        if hasattr(self.container, "adicionar_widget"):
            self.container.adicionar_widget(name, widget)
            self.container.setVisible(True)
            widget.setVisible(True)

    def remove_panel(self, name: str):
        """Remove um widget do painel lateral pelo nome/título da aba."""
        # Se precisar remover por título/nome na tab_bar
        if hasattr(self.container, "tab_bar") and hasattr(self.container, "stack"):
            for i in range(self.container.tab_bar.count()):
                if self.container.tab_bar.tabText(i) == name:
                    w = self.container.stack.widget(i)
                    self.container.stack.removeWidget(w)
                    self.container.tab_bar.removeTab(i)
                    w.deleteLater()
                    break
            if self.container.stack.count() == 0:
                self.container.stack.hide()

    def remover_widget_por_caminho(self, caminho: Path):
        """Repassa a solicitação de remoção por caminho para o container interno."""
        if hasattr(self.container, "remover_widget_por_caminho"):
            self.container.remover_widget_por_caminho(caminho)

    def clear_all(self):
        """Limpa todos os painéis/abas."""
        if hasattr(self.container, "limpar"):
            self.container.limpar()