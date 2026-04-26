import os
from PySide6 import QtWidgets, QtCore
from core.windows.janelas import JanelaBase


class Janela3D(JanelaBase):
    thresholdChanged = QtCore.Signal(int)
    presetChanged = QtCore.Signal(str)
    viewChanged = QtCore.Signal(str)

    def __init__(self, titulo: str, cor: str, parent=None):
        super().__init__(titulo, cor, parent)
        self._setup_ui()

    def _setup_ui(self):
        self.combo_presets = QtWidgets.QComboBox()
        self.combo_presets.setFixedWidth(120)

        self._popular_presets()

        index_bone = self.combo_presets.findText("bone", QtCore.Qt.MatchFixedString)
        if index_bone >= 0:
            self.combo_presets.setCurrentIndex(index_bone)

        self.combo_presets.currentTextChanged.connect(self.presetChanged.emit)

        self.slider_threshold = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_threshold.setRange(-1000, 3000)
        self.slider_threshold.setValue(400)
        self.slider_threshold.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.lbl_value = QtWidgets.QLabel("400 HU")
        self.lbl_value.setFixedWidth(60)
        self.lbl_value.setStyleSheet("color: #AAA; font-weight: bold;")

        self.slider_threshold.valueChanged.connect(self._on_threshold_ui_changed)

        self.combo_vistas = QtWidgets.QComboBox()
        self.combo_vistas.addItems(["Frente", "Posterior", "Superior", "Inferior", "Direito", "Esquerdo"])
        self.combo_vistas.setFixedWidth(100)

        index_frente = self.combo_vistas.findText("Frente")
        if index_frente >= 0:
            self.combo_vistas.setCurrentIndex(index_frente)

        self.combo_vistas.currentTextChanged.connect(self.viewChanged.emit)

        self.adicionar_controle(self.combo_presets)
        self.adicionar_controle(QtWidgets.QLabel(" Threshold:"))
        self.adicionar_controle(self.slider_threshold)
        self.adicionar_controle(self.lbl_value)
        self.adicionar_controle(self.combo_vistas)

    def _on_threshold_ui_changed(self, value):
        self.lbl_value.setText(f"{value} HU")
        self.thresholdChanged.emit(value)

    def _popular_presets(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_presets = os.path.abspath(os.path.join(base_dir, "..", "presets"))

        if os.path.exists(caminho_presets):
            files = [f.replace(".json", "") for f in os.listdir(caminho_presets) if f.endswith(".json")]
            if files:
                self.combo_presets.clear()
                self.combo_presets.addItems(sorted(files))