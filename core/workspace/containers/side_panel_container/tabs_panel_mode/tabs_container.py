from PySide6.QtWidgets import QTabWidget, QWidget


class TabsContainer(QTabWidget):
    """Container com abas (Tabs) para exibição e alternância de conteúdos

    no workspace, oferecendo uma alternativa ao modo Toolbox e Painel Flutuante.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("TabsContainer")
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(True)

    def add_workspace_tab(self, widget: QWidget, title: str):
        """Adiciona um novo widget com uma aba correspondente ao container."""
        return self.addTab(widget, title)

    def remove_workspace_tab(self, index: int):
        """Remove a aba correspondente ao índice informado."""
        widget = self.widget(index)
        if widget:
            self.removeTab(index)
            widget.deleteLater()