from PySide6 import QtWidgets, QtCore


class StatusBarManager(QtWidgets.QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.message_label = QtWidgets.QLabel("Pronto")
        self.addWidget(self.message_label)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedSize(150, 16)
        self.progress_bar.hide()
        self.addPermanentWidget(self.progress_bar)

    def start_loading(self, message: str):
        """Ativa o feedback visual de carregamento."""
        self.message_label.setText(message)
        self.progress_bar.show()
        QtCore.QCoreApplication.processEvents()

    def stop_loading(self):
        """Desativa o feedback visual."""
        self.progress_bar.hide()
        self.message_label.setText("Pronto")

    def update_message(self, message: str):
        """Atualiza a mensagem de status atual."""
        self.message_label.setText(message)