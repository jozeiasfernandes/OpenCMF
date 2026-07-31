from PySide6 import QtWidgets

class BaseSidePanelMode:
    """Classe base abstrata (Estratégia) para os diferentes modos de exibição do painel lateral."""

    def __init__(self, container):
        self.container = container

    def add_panel(self, panel_id: str, widget: QtWidgets.QWidget, title: str):
        """Adiciona um painel ao modo atual."""
        raise NotImplementedError

    def remove_panel(self, panel_id: str):
        """Remove um painel do modo atual."""
        raise NotImplementedError

    def clear(self):
        """Limpa todos os painéis do modo atual."""
        raise NotImplementedError