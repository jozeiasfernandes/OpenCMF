from PySide6 import QtWidgets
from .central_area_container import CentralAreaContainer

class CentralAreaManager:
    """
    Gerencia a lógica de exibição e ciclo de vida dos widgets na área central.
    """
    def __init__(self, parent=None):
        self.container = CentralAreaContainer(parent)

    def set_view(self, widget: QtWidgets.QWidget):
        """Define o widget ativo na área central, adicionando-o diretamente ao container sem limpezas redundantes."""
        if widget:
            self.container.add_view(widget)

    def clear(self):
        """Remove todos os widgets da área central sem destruí-los, permitindo reuso em cache."""
        container = self.get_container()
        if container and isinstance(container, QtWidgets.QStackedWidget):
            while container.count() > 0:
                widget = container.widget(0)
                if widget:
                    container.removeWidget(widget)
                    widget.setParent(None)

    def get_container(self) -> CentralAreaContainer:
        return self.container