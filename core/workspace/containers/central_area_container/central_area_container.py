from PySide6 import QtWidgets


class CentralAreaContainer(QtWidgets.QStackedWidget):
    """
    Container visual que hospeda o viewport principal da aplicação.
    Gerencia o empilhamento de widgets de módulos de forma limpa e isolada.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

    def add_view(self, widget: QtWidgets.QWidget):
        """Adiciona e define a view ativa, removendo e limpando views antigas do stack."""
        if not widget:
            return

        # Remove e limpa todos os widgets anteriores do stack
        while self.count() > 0:
            old_widget = self.widget(0)
            if old_widget:
                self.removeWidget(old_widget)
                old_widget.setParent(None)
                old_widget.deleteLater()

        # Adiciona o novo widget e o define como atual
        self.addWidget(widget)
        self.setCurrentWidget(widget)

        # Força a atualização imediata para evitar artefatos visuais
        widget.show()
        widget.repaint()

    def remove_view(self, widget: QtWidgets.QWidget):
        """Remove a vista do stack e assegura a destruição do widget."""
        if not widget:
            return

        index = self.indexOf(widget)
        if index >= 0:
            self.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()