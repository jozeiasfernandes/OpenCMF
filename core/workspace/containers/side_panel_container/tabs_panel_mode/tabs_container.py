from PySide6.QtWidgets import QTabWidget, QWidget
from typing import Dict, Optional


class TabsContainer(QTabWidget):
    """
    Container especializado no Modo Tabs para exibição e alternância de conteúdos
    no painel lateral da workspace, com abas orientadas à direita (East).
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("TabsContainer")
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(True)
        self.setTabPosition(QTabWidget.East)

        # Mapeamento interno para rastrear painéis por ID com segurança
        self._panel_widgets: Dict[str, QWidget] = {}

    def add_workspace_tab(self, panel_id: str, widget: QWidget, title: str):
        """Adiciona ou substitui um widget associado a uma aba no container."""
        if panel_id in self._panel_widgets:
            self.remove_workspace_tab(panel_id)

        self._panel_widgets[panel_id] = widget
        index = self.addTab(widget, title)
        widget.setVisible(True)
        return index

    def remove_workspace_tab(self, panel_id: str):
        """Remove a aba e o widget correspondente ao identificador informado."""
        widget = self._panel_widgets.pop(panel_id, None)
        if widget:
            index = self.indexOf(widget)
            if index != -1:
                self.removeTab(index)

            if hasattr(widget, 'dispose') and callable(widget.dispose):
                try:
                    widget.dispose()
                except Exception:
                    pass

            widget.setParent(None)
            widget.deleteLater()

    def clear_all_tabs(self):
        """Remove todas as abas e limpa os registros internos."""
        for panel_id in list(self._panel_widgets.keys()):
            self.remove_workspace_tab(panel_id)

    def get_widget_by_id(self, panel_id: str) -> Optional[QWidget]:
        """Retorna o widget associado ao ID do painel."""
        return self._panel_widgets.get(panel_id)