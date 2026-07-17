from PySide6 import QtWidgets, QtCore

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
        self.removeWidget(widget)
        widget.deleteLater()