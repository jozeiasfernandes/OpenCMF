from PySide6 import QtWidgets, QtCore
from core.windows.janelas import JanelaBase

class Janela3D(JanelaBase):
    thresholdChanged = QtCore.Signal(int)
    viewChanged = QtCore.Signal(str)

    def __init__(self, titulo: str, cor: str, parent=None):
        super().__init__(titulo, cor, parent)
        self._setup_ui()

    def _setup_ui(self):
        self.combo_presets = QtWidgets.QComboBox()
        self.combo_presets.addItems(["Osso", "Tecido Mole", "Pele", "MIP"])
        self.combo_presets.setFixedWidth(100)

        self.slider_threshold = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_threshold.setRange(0, 3000)
        self.slider_threshold.setValue(400)
        self.slider_threshold.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.slider_threshold.valueChanged.connect(self.thresholdChanged.emit)

        self.combo_vistas = QtWidgets.QComboBox()
        self.combo_vistas.addItems(["Frente", "Posterior", "Superior", "Inferior", "Direito", "Esquerdo"])
        self.combo_vistas.setFixedWidth(100)
        self.combo_vistas.currentTextChanged.connect(self.viewChanged.emit)

        self.adicionar_controle(self.combo_presets)
        self.adicionar_controle(QtWidgets.QLabel(" Threshold:"))
        self.adicionar_controle(self.slider_threshold)
        self.adicionar_controle(self.combo_vistas)