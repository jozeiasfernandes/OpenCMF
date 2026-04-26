from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path


class Janela_Creditos(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Créditos - OpenCFM")
        self.setFixedSize(500, 480)  # Aumentado um pouco para acomodar o texto com folga
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 1. Label da Imagem (OpenCFM.png)
        self.lbl_logo = QtWidgets.QLabel()
        self.lbl_logo.setAlignment(QtCore.Qt.AlignCenter)

        # Caminho subindo um nível para achar a pasta icons
        path_logo = Path(__file__).parent.parent / "icons" / "OpenCFM.png"

        if path_logo.exists():
            pixmap = QtGui.QPixmap(str(path_logo))
            self.lbl_logo.setPixmap(pixmap.scaled(
                430, 180,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            ))
        else:
            self.lbl_logo.setText("<h2>OpenCFM</h2>")

        # 2. Label de Texto com link e correções de tags HTML
        self.lbl_texto = QtWidgets.QLabel(
            "<h3>Criado por Jozeias Fernandes</h3>"
            "<p>Contribuições: Sem contribuições ainda</p>"
            "<p>Agradecimentos: Sem agradecimentos ainda</p>"
            "<p>Comunidade:</p>"
            "<p> <a href='https://github.com/jozeiasfernandes/OpenCMF' "
            "style='color: #3498db; text-decoration: none;'>GitHub / OpenCMF</a></p>"
        )

        self.lbl_texto.setWordWrap(True)
        self.lbl_texto.setAlignment(QtCore.Qt.AlignLeft)
        self.lbl_texto.setTextFormat(QtCore.Qt.RichText)

        # Habilita a abertura de links externos no navegador padrão
        self.lbl_texto.setOpenExternalLinks(True)

        # 3. Botão Fechar
        self.btn_fechar = QtWidgets.QPushButton("FECHAR")
        self.btn_fechar.setFixedWidth(120)
        self.btn_fechar.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_fechar.clicked.connect(self.accept)

        # Organização no layout
        layout.addWidget(self.lbl_logo)
        layout.addWidget(self.lbl_texto)
        layout.addStretch()
        layout.addWidget(self.btn_fechar, alignment=QtCore.Qt.AlignCenter)