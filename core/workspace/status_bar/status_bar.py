from PySide6 import QtWidgets, QtCore

class StatusBarManager(QtWidgets.QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("QStatusBar::item { border: none; }")

        self.message_label = QtWidgets.QLabel("Pronto")
        self.addWidget(self.message_label, stretch=1)

        self.progress_bar = QtWidgets.QProgressBar()
        # Se quiser modo infinito, use range(0,0). Se for progresso real, ajuste depois.
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedSize(150, 16)
        self.progress_bar.setVisible(False)
        self.addPermanentWidget(self.progress_bar)

    def start_loading(self, message: str):
        """Ativa o feedback visual de carregamento."""
        self.message_label.setText(message)
        self.progress_bar.setVisible(True)

    def stop_loading(self):
        """Desativa o feedback visual."""
        self.progress_bar.setVisible(False)
        self.message_label.setText("Pronto")

    def showMessage(self, message: str, timeout: int = 0):
        """
        Sobrescreve/complementa o método nativo showMessage para
        atualizar o seu label personalizado.
        """
        self.message_label.setText(message)
        # Chama o método da classe pai para manter a compatibilidade
        super().showMessage(message, timeout)

    def update_message(self, message: str, timeout: int = 0):
        """Método de conveniência que chama o showMessage."""
        self.showMessage(message, timeout)