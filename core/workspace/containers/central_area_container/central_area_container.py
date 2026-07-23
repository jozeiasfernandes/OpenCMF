from PySide6 import QtWidgets

class CentralAreaContainer(QtWidgets.QStackedWidget):
    """
    Container visual que hospeda o viewport principal da aplicação.
    Gerencia o empilhamento de widgets de módulos.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def add_view(self, widget: QtWidgets.QWidget):
        self.addWidget(widget)
        self.setCurrentWidget(widget)

    def remove_view(self, widget: QtWidgets.QWidget):
        """Remove a vista do stack e assegura a destruição do widget anterior para evitar sobreposições."""
        if widget:
            self.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()