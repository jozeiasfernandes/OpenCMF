from PySide6 import QtWidgets
from .central_area_container import CentralAreaContainer

class CentralAreaManager:
    """
    Gerencia a lógica de exibição e ciclo de vida dos widgets na área central.
    """
    def __init__(self, parent=None):
        self.container = CentralAreaContainer(parent)

    def set_view(self, widget: QtWidgets.QWidget):
        """Define o widget ativo na área central, limpando o anterior."""
        self.clear()
        self.container.add_view(widget)

    def clear(self):
        """Limpa todos os widgets da área central de forma imediata e segura."""
        while self.container.count() > 0:
            widget = self.container.widget(0)
            if widget:
                self.container.remove_view(widget)
                # Garante remoção síncrona/imediata se necessário
                widget.setParent(None)
                widget.deleteLater()

    def get_container(self) -> CentralAreaContainer:
        return self.container