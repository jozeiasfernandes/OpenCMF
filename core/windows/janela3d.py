from PySide6 import QtWidgets, QtCore
from core.windows.janelas import JanelaBase


class Janela3D(JanelaBase):
    thresholdChanged = QtCore.Signal(int)

    def __init__(self, titulo: str, cor: str, parent=None):
        super().__init__(titulo, cor, parent)
        self._init_specific_widgets()

    def _init_specific_widgets(self):
        self.combo_presets = QtWidgets.QComboBox()
        self.combo_presets.addItems(["Osso", "Tecido Mole", "Pele", "MIP"])
        self.combo_presets.setFixedWidth(100)

        self.slider_threshold = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_threshold.setRange(0, 3000)
        self.slider_threshold.setValue(400)

        self.btn_reset = QtWidgets.QToolButton()
        self.btn_reset.setText("Reset")

        self.adicionar_controle(self.combo_presets)
        self.adicionar_controle(QtWidgets.QLabel("Threshold:"))
        self.adicionar_controle(self.slider_threshold)

        self.layout_barra.addStretch()

        for vista in ["F", "S", "E", "D"]:
            btn = QtWidgets.QToolButton()
            btn.setText(vista)
            btn.setFixedSize(22, 22)
            self.adicionar_controle(btn)

        self.adicionar_controle(self.btn_reset)
        self.slider_threshold.valueChanged.connect(self.thresholdChanged.emit)