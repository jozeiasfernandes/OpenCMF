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
        """Remove todos os widgets da área central sem destruí-los, permitindo reuso em cache."""
        layout = self.get_container().layout()
        if isinstance(layout, QtWidgets.QStackedWidget):
            while layout.count() > 0:
                widget = layout.widget(0)
                if widget:
                    layout.removeWidget(widget)
                    widget.setParent(None)
        elif layout:
            while layout.count() > 0:
                item = layout.takeAt(0)
                if item and item.widget():
                    widget = item.widget()
                    widget.setParent(None)

    def get_container(self) -> CentralAreaContainer:
        return self.container