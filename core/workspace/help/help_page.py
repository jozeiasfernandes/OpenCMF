from PySide6 import QtWidgets, QtCore, QtGui


class HelpPage(QtWidgets.QDialog):
    """Janela de Ajuda do Software."""

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self.setWindowTitle("Ajuda")
        self.resize(600, 400)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)

        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface da página de ajuda."""
        layout = QtWidgets.QVBoxLayout(self)

        # Título
        title = QtWidgets.QLabel("Central de Ajuda")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Área de texto (suporta HTML básico)
        self.browser = QtWidgets.QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setHtml("""
            <h1>Bem-vindo ao Workspace</h1>
            <p>Esta é a página de ajuda do seu software.</p>
            <ul>
                <li><b>Carregamento:</b> Use o ícone de engrenagens para gerenciar componentes.</li>
                <li><b>Configurações:</b> Ajuste suas preferências no ícone de ajustes.</li>
            </ul>
            <p>Se precisar de suporte, entre em contato com a equipe de desenvolvimento.</p>
        """)
        layout.addWidget(self.browser)

        # Botão de Fechar
        self.btn_close = QtWidgets.QPushButton("Fechar")
        self.btn_close.setFixedWidth(100)
        self.btn_close.clicked.connect(self.accept)

        layout.addWidget(self.btn_close, alignment=QtCore.Qt.AlignRight)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = HelpPage()
    window.show()
    sys.exit(app.exec())