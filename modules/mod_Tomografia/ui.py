# ui.py - Interface do Módulo de Tomografia
from PySide6 import QtWidgets, QtCore, QtGui
from typing import Dict, Callable


class TomografiaUI:
    def __init__(self):
        # Widgets de Gestão
        self.edit_dicom = QtWidgets.QLineEdit()
        self.btn_validar = QtWidgets.QPushButton("🔍 Validar DICOM")
        self.btn_carregar = QtWidgets.QPushButton("⌛ Carregar DICOM")
        self.btn_finalizar = QtWidgets.QPushButton("Finalizar Etapa")

        # Widgets de Window/Level (Brilho/Contraste)
        self.spin_window = QtWidgets.QSpinBox()
        self.slider_window = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.spin_level = QtWidgets.QSpinBox()
        self.slider_level = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        # Widgets de LUT
        self.combo_lut = QtWidgets.QComboBox()
        self.check_interpolate = QtWidgets.QCheckBox("Interpolar Cores")

        self.layout_filtros = None

    def setup_toolboxes(self,
                        on_buscar: Callable,
                        on_validar: Callable,
                        on_carregar: Callable,
                        on_wl_manual: Callable,  # Nova função para Window/Level
                        on_finalizar: Callable) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Abrir": self._create_aba_abrir(on_buscar, on_validar, on_carregar, on_finalizar),
            "Filtrar": self._create_aba_filtrar(on_wl_manual)
        }

    def _create_aba_abrir(self, on_buscar, on_validar, on_carregar, on_finalizar) -> QtWidgets.QWidget:
        aba = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(aba)
        layout.setSpacing(8)

        layout.addWidget(QtWidgets.QLabel("<b>GESTÃO DE ARQUIVOS</b>"))

        # Seleção de Pasta
        linha_busca = QtWidgets.QWidget()
        h_lay = QtWidgets.QHBoxLayout(linha_busca)
        h_lay.setContentsMargins(0, 0, 0, 0)

        btn_pasta = QtWidgets.QPushButton("...")
        btn_pasta.setFixedWidth(30)
        btn_pasta.clicked.connect(on_buscar)

        h_lay.addWidget(self.edit_dicom)
        h_lay.addWidget(btn_pasta)

        layout.addWidget(QtWidgets.QLabel("Caminho DICOM:"))
        layout.addWidget(linha_busca)

        # Botões de Ação
        self.btn_validar.clicked.connect(on_validar)
        layout.addWidget(self.btn_validar)

        self.btn_carregar.setEnabled(False)
        self.btn_carregar.setStyleSheet("font-weight: bold; background-color: #2980b9; color: white;")
        self.btn_carregar.clicked.connect(on_carregar)
        layout.addWidget(self.btn_carregar)

        layout.addStretch()

        self.btn_finalizar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_finalizar.clicked.connect(on_finalizar)
        layout.addWidget(self.btn_finalizar)

        return aba

    def _create_aba_filtrar(self, on_wl_manual) -> QtWidgets.QWidget:
        aba = QtWidgets.QWidget()
        self.layout_filtros = QtWidgets.QVBoxLayout(aba)
        self.layout_filtros.setSpacing(12)

        self.layout_filtros.addWidget(QtWidgets.QLabel("<b>CONTROLE DE VISUALIZAÇÃO</b>"))

        # --- SEÇÃO WINDOW/LEVEL (Brilho/Contraste) ---
        group_wl = QtWidgets.QGroupBox("Window / Level Manual")
        layout_wl = QtWidgets.QVBoxLayout(group_wl)

        # Window (Contraste)
        layout_w = QtWidgets.QHBoxLayout()
        self.spin_window.setRange(1, 5000)
        self.spin_window.setValue(1500)
        self.slider_window.setRange(1, 5000)
        self.slider_window.setValue(1500)

        layout_w.addWidget(QtWidgets.QLabel("W:"))
        layout_w.addWidget(self.spin_window)
        layout_w.addWidget(self.slider_window)
        layout_wl.addLayout(layout_w)

        # Level (Brilho)
        layout_l = QtWidgets.QHBoxLayout()
        self.spin_level.setRange(-1000, 3000)
        self.spin_level.setValue(300)
        self.slider_level.setRange(-1000, 3000)
        self.slider_level.setValue(300)

        layout_l.addWidget(QtWidgets.QLabel("L :"))
        layout_l.addWidget(self.spin_level)
        layout_l.addWidget(self.slider_level)
        layout_wl.addLayout(layout_l)

        # Sincronização Interna dos Sliders com Spinboxes
        self.slider_window.valueChanged.connect(self.spin_window.setValue)
        self.spin_window.valueChanged.connect(self.slider_window.setValue)
        self.slider_level.valueChanged.connect(self.spin_level.setValue)
        self.spin_level.valueChanged.connect(self.slider_level.setValue)

        # Conexão com a função de atualização do VTK
        self.slider_window.valueChanged.connect(
            lambda: on_wl_manual(self.slider_window.value(), self.slider_level.value()))
        self.slider_level.valueChanged.connect(
            lambda: on_wl_manual(self.slider_window.value(), self.slider_level.value()))

        self.layout_filtros.addWidget(group_wl)

        # --- SEÇÃO LOOKUP TABLE (Cores) ---
        group_lut = QtWidgets.QGroupBox("Tabela de Cores (LUT)")
        layout_lut = QtWidgets.QVBoxLayout(group_lut)

        self.combo_lut.addItems(["Grey", "Bone", "Cool", "Hot", "Rainbow"])
        self.check_interpolate.setChecked(True)

        layout_lut.addWidget(QtWidgets.QLabel("Paleta:"))
        layout_lut.addWidget(self.combo_lut)
        layout_lut.addWidget(self.check_interpolate)

        self.layout_filtros.addWidget(group_lut)

        self.layout_filtros.addStretch()
        return aba


    def update_status_validado(self):
        self.btn_validar.setText("✅ DICOM Validado")
        self.btn_validar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_carregar.setEnabled(True)

    def update_status_erro(self):
        self.btn_validar.setText("❌ Erro na Pasta")
        self.btn_validar.setStyleSheet("background-color: #c0392b; color: white;")

    def update_status_carregado(self):
        self.btn_carregar.setText("✅ Carregamento concluído")
        self.btn_carregar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")

    # Dentro de ui.py
    def update_wl_ui(self, window: float, level: float):
        # Usar blockSignals nos componentes individuais se necessário
        self.slider_window.blockSignals(True)
        self.slider_level.blockSignals(True)

        self.slider_window.setValue(int(window))
        self.slider_level.setValue(int(level))
        self.spin_window.setValue(int(window))
        self.spin_level.setValue(int(level))

        self.slider_window.blockSignals(False)
        self.slider_level.blockSignals(False)