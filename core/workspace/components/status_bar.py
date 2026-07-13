from PySide6 import QtWidgets, QtCore


class StatusBarManager(QtWidgets.QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Opcional: remover a borda padrão para um visual mais clean
        self.setStyleSheet("QStatusBar::item { border: none; }")

        self.message_label = QtWidgets.QLabel("Pronto")
        self.addWidget(self.message_label, stretch=1)  # stretch=1 permite que a mensagem ocupe o espaço extra

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 0)  # Determinate mode (loading infinito)
        self.progress_bar.setFixedSize(150, 16)
        self.progress_bar.setVisible(False)  # Usar setVisible é ligeiramente mais idiomático
        self.addPermanentWidget(self.progress_bar)

    def start_loading(self, message: str):
        """Ativa o feedback visual de carregamento."""
        self.message_label.setText(message)
        self.progress_bar.setVisible(True)
        # NOTA: processEvents() pode causar reentrância e instabilidade.
        # Prefira deixar o loop de eventos processar naturalmente.

    def stop_loading(self):
        """Desativa o feedback visual."""
        self.progress_bar.setVisible(False)
        self.message_label.setText("Pronto")

    def update_message(self, message: str, timeout: int = 0):
        """
        Atualiza a mensagem com suporte a timeout.
        O método nativo showMessage é mais robusto para mensagens temporárias.
        """
        if timeout > 0:
            self.showMessage(message, timeout)
        else:
            self.message_label.setText(message)