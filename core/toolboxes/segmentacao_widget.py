from PySide6 import QtWidgets, QtCore
from modulos.mod_Paciente.ui_components import criar_linha_arquivo

class SegmentacaoWidget(QtWidgets.QWidget):
    pathChanged = QtCore.Signal(str)
    thresholdChanged = QtCore.Signal(int)
    solicitarMascara = QtCore.Signal()
    solicitarExportarSTL = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)

        group_arq = QtWidgets.QGroupBox("Fonte de Dados")
        lay_arq = QtWidgets.QVBoxLayout(group_arq)
        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_tomografia.setPlaceholderText("Caminho da pasta DICOM...")
        self.edit_tomografia.textChanged.connect(self.pathChanged.emit)

        def abrir_seletor():
            p = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecionar Pasta DICOM")
            if p: self.edit_tomografia.setText(p)

        lay_arq.addWidget(criar_linha_arquivo(self.edit_tomografia, abrir_seletor, True))
        layout.addWidget(group_arq)

        group_config = QtWidgets.QGroupBox("Configurações da malha")
        grid_layout = QtWidgets.QGridLayout(group_config)
        grid_layout.setSpacing(10)

        lbl_densidade = QtWidgets.QLabel("Filtro de Densidade:")
        self.slider_hu = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_hu.setRange(-1000, 3000)
        self.slider_hu.setValue(226)
        self.slider_hu.valueChanged.connect(self._on_slider_moved)

        self.lbl_hu_value = QtWidgets.QLabel("226 HU")
        self.lbl_hu_value.setStyleSheet("font-weight: bold;")
        self.lbl_hu_value.setFixedWidth(60)

        grid_layout.addWidget(lbl_densidade, 0, 0)
        grid_layout.addWidget(self.slider_hu, 0, 1)
        grid_layout.addWidget(self.lbl_hu_value, 0, 2)

        lbl_resolucao = QtWidgets.QLabel("Resolução:")
        self.combo_qualidade = QtWidgets.QComboBox()
        self.combo_qualidade.addItems(["Alta", "Média", "Baixa"])
        self.combo_qualidade.setCurrentIndex(1)

        grid_layout.addWidget(lbl_resolucao, 1, 0)
        grid_layout.addWidget(self.combo_qualidade, 1, 1, 1, 2)

        layout.addWidget(group_config)

        self.btn_preview = QtWidgets.QPushButton(" Gerar Máscara")
        self.btn_preview.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        self.btn_preview.setMinimumHeight(35)
        self.btn_preview.clicked.connect(self.solicitarMascara.emit)
        layout.addWidget(self.btn_preview)

        layout.addStretch()

        self.btn_stl = QtWidgets.QPushButton(" Exportar STL")
        self.btn_stl.setMinimumHeight(45)
        self.btn_stl.setStyleSheet("""
            QPushButton {
                background-color: #2d5a27; 
                color: white; 
                font-weight: bold; 
                font-size: 13px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a7532;
            }
            QPushButton:pressed {
                background-color: #1e3d1a;
            }
        """)
        self.btn_stl.clicked.connect(self.solicitarExportarSTL.emit)
        layout.addWidget(self.btn_stl)

    def _on_slider_moved(self, val):
        self.lbl_hu_value.setText(f"{val} HU")
        self.thresholdChanged.emit(val)

    def set_path(self, caminho: str):
        self.edit_tomografia.blockSignals(True)
        self.edit_tomografia.setText(caminho)
        self.edit_tomografia.blockSignals(False)

    def get_value(self) -> int:
        return self.slider_hu.value()

    def get_qualidade_index(self) -> int:
        return self.combo_qualidade.currentIndex()