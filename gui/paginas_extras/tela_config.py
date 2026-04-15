import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

class PaginaConfig(QtWidgets.QWidget):
    voltar_solicitado = QtCore.Signal()
    tema_alterado = QtCore.Signal(str)
    idioma_alterado = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        self.main_layout.setSpacing(30)

        self._add_title()
        self._tema_idioma()
        self.main_layout.addStretch()
        self._btn_fechar()

    def _add_title(self):
        title = QtWidgets.QLabel("<h2>Configurações</h2>")
        self.main_layout.addWidget(title, alignment=QtCore.Qt.AlignTop)

    def _tema_idioma(self):
        form_container = QtWidgets.QFormLayout()
        form_container.setSpacing(20)
        form_container.setLabelAlignment(QtCore.Qt.AlignLeft)

        self.combo_temas = QtWidgets.QComboBox()
        self.combo_temas.setMinimumHeight(35)
        self._carregar_temas()
        self.combo_temas.currentIndexChanged.connect(self._on_tema_changed)

        self.combo_idioma = QtWidgets.QComboBox()
        self.combo_idioma.setMinimumHeight(35)
        self.combo_idioma.addItems(["Português (Brasil)", "English", "Español"])
        self.combo_idioma.currentTextChanged.connect(self.idioma_alterado.emit)

        form_container.addRow(QtWidgets.QLabel("Tema do Sistema:"), self.combo_temas)
        form_container.addRow(QtWidgets.QLabel("Idioma:"), self.combo_idioma)

        self.main_layout.addLayout(form_container)

    def _btn_fechar(self):
        self.btn_fechar = QtWidgets.QPushButton("Fechar")
        self.btn_fechar.setFixedSize(150, 45)
        self.btn_fechar.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_fechar.clicked.connect(self.voltar_solicitado.emit)
        self.main_layout.addWidget(self.btn_fechar, alignment=QtCore.Qt.AlignCenter)

    def _carregar_temas(self):
        # CORREÇÃO: Subir 3 níveis para sair de 'gui/paginas_extras' e chegar na raiz
        # parent 1: paginas_extras | parent 2: gui | parent 3: raiz (OpenCMF)
        base_dir = Path(__file__).resolve().parent.parent.parent
        themes_dir = base_dir / "temas"

        if not themes_dir.exists():
            logging.error(f"Diretório não encontrado: {themes_dir}")
            self.combo_temas.addItem("Padrão (Pasta não encontrada)", userData=None)
            return

        qss_files = list(themes_dir.glob("*.qss"))

        if not qss_files:
            self.combo_temas.addItem("Padrão (Vazio)", userData=None)
            return

        # Bloqueia sinais para não disparar o evento de mudança enquanto carrega a lista
        self.combo_temas.blockSignals(True)
        for qss in qss_files:
            display_name = qss.stem.replace("_", " ").capitalize()
            self.combo_temas.addItem(display_name, userData=str(qss))
        self.combo_temas.blockSignals(False)

    def _on_tema_changed(self):
        path_qss = self.combo_temas.currentData()
        if path_qss:
            self.tema_alterado.emit(path_qss)

    def get_settings(self) -> dict:
        return {
            "tema_caminho": self.combo_temas.currentData(),
            "idioma": self.combo_idioma.currentText()
        }