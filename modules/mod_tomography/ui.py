from PySide6 import QtWidgets, QtCore, QtGui
from typing import Dict, Callable

class TomografiaUI:
    def __init__(self):
        self.edit_dicom = QtWidgets.QLineEdit()
        self.btn_validar = QtWidgets.QPushButton("🔍 Validar Pasta DICOM")
        self.btn_carregar = QtWidgets.QPushButton("⌛ Carregar para Visualização")
        self.btn_gerar_vti = QtWidgets.QPushButton("💾 Gerar Volume (.vti)")
        self.btn_finalizar = QtWidgets.QPushButton("Finalizar Etapa")

        self.spin_window = QtWidgets.QSpinBox()
        self.slider_window = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.spin_level = QtWidgets.QSpinBox()
        self.slider_level = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        self.combo_lut = QtWidgets.QComboBox()
        self.check_interpolate = QtWidgets.QCheckBox("Interpolar Cores")

    def setup_toolboxes(self,
                        on_buscar: Callable,
                        on_validar: Callable,
                        on_carregar: Callable,
                        on_gerar_vti: Callable,
                        on_wl_manual: Callable,
                        on_finalizar: Callable) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Arquivos": self._create_aba_abrir(on_buscar, on_validar, on_carregar, on_gerar_vti, on_finalizar),
            "Visualização": self._create_aba_filtrar(on_wl_manual)
        }

    def _create_aba_abrir(self, on_buscar, on_validar, on_carregar, on_gerar_vti, on_finalizar) -> QtWidgets.QWidget:
        aba = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(aba)
        layout.setSpacing(10)

        layout.addWidget(QtWidgets.QLabel("<b>GESTÃO DE DADOS</b>"))

        linha_busca = QtWidgets.QWidget()
        h_lay = QtWidgets.QHBoxLayout(linha_busca)
        h_lay.setContentsMargins(0, 0, 0, 0)
        btn_pasta = QtWidgets.QPushButton("...")
        btn_pasta.setFixedWidth(30)
        btn_pasta.clicked.connect(on_buscar)
        h_lay.addWidget(self.edit_dicom)
        h_lay.addWidget(btn_pasta)

        layout.addWidget(QtWidgets.QLabel("Pasta dos arquivos DICOM:"))
        layout.addWidget(linha_busca)

        self.btn_validar.clicked.connect(on_validar)
        layout.addWidget(self.btn_validar)

        self.btn_carregar.setEnabled(False)
        self.btn_carregar.setStyleSheet("font-weight: bold; padding: 5px;")
        self.btn_carregar.clicked.connect(on_carregar)
        layout.addWidget(self.btn_carregar)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        self.btn_gerar_vti.setEnabled(False)
        self.btn_gerar_vti.setStyleSheet("color: #3498db; font-weight: bold;")
        self.btn_gerar_vti.clicked.connect(on_gerar_vti)
        layout.addWidget(self.btn_gerar_vti)

        layout.addStretch()

        self.btn_finalizar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        self.btn_finalizar.clicked.connect(on_finalizar)
        layout.addWidget(self.btn_finalizar)

        return aba

    def _create_aba_filtrar(self, on_wl_manual) -> QtWidgets.QWidget:
        aba = QtWidgets.QWidget()
        layout_filtros = QtWidgets.QVBoxLayout(aba)
        layout_filtros.setSpacing(12)

        layout_filtros.addWidget(QtWidgets.QLabel("<b>CONTRASTE E BRILHO</b>"))

        group_wl = QtWidgets.QGroupBox("Ajuste Manual (HU)")
        layout_wl = QtWidgets.QVBoxLayout(group_wl)

        for label, slider, spin, r_min, r_max, val in [
            ("W:", self.slider_window, self.spin_window, 1, 5000, 1500),
            ("L:", self.slider_level, self.spin_level, -1000, 3000, 300)
        ]:
            lay = QtWidgets.QHBoxLayout()
            spin.setRange(r_min, r_max)
            spin.setValue(val)
            slider.setRange(r_min, r_max)
            slider.setValue(val)
            lay.addWidget(QtWidgets.QLabel(label))
            lay.addWidget(spin)
            lay.addWidget(slider)
            layout_wl.addLayout(lay)

        self.slider_window.valueChanged.connect(self.spin_window.setValue)
        self.spin_window.valueChanged.connect(self.slider_window.setValue)
        self.slider_level.valueChanged.connect(self.spin_level.setValue)
        self.spin_level.valueChanged.connect(self.slider_level.setValue)

        self.slider_window.valueChanged.connect(lambda: on_wl_manual(self.slider_window.value(), self.slider_level.value()))
        self.slider_level.valueChanged.connect(lambda: on_wl_manual(self.slider_window.value(), self.slider_level.value()))

        layout_filtros.addWidget(group_wl)

        group_lut = QtWidgets.QGroupBox("Paleta de Cores")
        layout_lut = QtWidgets.QVBoxLayout(group_lut)
        self.combo_lut.addItems(["Grey", "Bone", "Cool", "Hot", "Rainbow"])
        layout_lut.addWidget(self.combo_lut)
        layout_lut.addWidget(self.check_interpolate)
        layout_filtros.addWidget(group_lut)

        layout_filtros.addStretch()
        return aba

    def update_status_validado(self):
        self.btn_validar.setText("✅ DICOM Validado")
        self.btn_validar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_carregar.setEnabled(True)

    def update_status_carregado(self):
        self.btn_carregar.setText("✅ Volume em Memória")
        self.btn_carregar.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        self.btn_gerar_vti.setEnabled(True)

    def update_status_vti_gerado(self):
        self.btn_gerar_vti.setText("✅ Volume .VTI Salvo")
        self.btn_gerar_vti.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")

    def update_wl_ui(self, window: float, level: float):
        self.slider_window.blockSignals(True)
        self.slider_level.blockSignals(True)
        val_w, val_l = int(window), int(level)
        self.slider_window.setValue(val_w)
        self.spin_window.setValue(val_w)
        self.slider_level.setValue(val_l)
        self.spin_level.setValue(val_l)
        self.slider_window.blockSignals(False)
        self.slider_level.blockSignals(False)