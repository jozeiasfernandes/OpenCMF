from PySide6 import QtWidgets, QtCore
from core import tr
from core.settings.settings_app_manager import settings


class TabSidePanel(QtWidgets.QWidget):
    """Aba de configurações para o Side Panel."""

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._carregar_valores()
        self._conectar_sinais()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.lbl_title = QtWidgets.QLabel(tr("configs.side_panel", "Configurações do Side Panel"))
        layout.addWidget(self.lbl_title)

        # Opção de visibilidade padrão
        self.checkbox_visibilidade = QtWidgets.QCheckBox(
            tr("configs.side_panel.show_by_default", "Mostrar Side Panel por padrão")
        )
        layout.addWidget(self.checkbox_visibilidade)

        # Configuração da largura estimada/inicial com Slider e SpinBox sincronizados
        width_layout = QtWidgets.QHBoxLayout()
        self.lbl_width = QtWidgets.QLabel(tr("configs.side_panel.width", "Largura inicial:"))

        self.spin_width = QtWidgets.QSpinBox()
        self.spin_width.setRange(150, 600)
        self.spin_width.setSuffix(" px")
        self.spin_width.setFixedWidth(90)

        self.slider_width = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_width.setRange(150, 600)
        self.slider_width.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider_width.setTickInterval(50)

        # Sincronização entre o Slider e o SpinBox
        self.slider_width.valueChanged.connect(self.spin_width.setValue)
        self.spin_width.valueChanged.connect(self.slider_width.setValue)

        width_layout.addWidget(self.lbl_width)
        width_layout.addWidget(self.slider_width)
        width_layout.addWidget(self.spin_width)
        layout.addLayout(width_layout)

        # Configuração do modo de exibição / estilo de container (Tab Widget vs Toolbox)
        mode_layout = QtWidgets.QHBoxLayout()
        self.lbl_mode = QtWidgets.QLabel(tr("configs.side_panel.mode", "Modo do Container:"))
        self.combo_mode = QtWidgets.QComboBox()
        self.combo_mode.addItem(tr("configs.side_panel.mode.tabs", "Abas Laterais (East)"), "tabs")
        self.combo_mode.addItem(tr("configs.side_panel.mode.toolbox", "Painéis Empilhados (Toolbox / Colapsável)"),
                                "toolbox")
        mode_layout.addWidget(self.lbl_mode)
        mode_layout.addWidget(self.combo_mode)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        layout.addStretch()

    def _carregar_valores(self):
        """Carrega os valores salvos no settings_manager para os widgets."""
        self.checkbox_visibilidade.setChecked(settings.side_panel_show_by_default)

        # Define valor no slider (o que atualiza automaticamente o spinbox pela conexão)
        self.slider_width.setValue(settings.side_panel_width)

        # Seleciona o item correspondente no combobox pelo dado armazenado
        index = self.combo_mode.findData(settings.side_panel_mode)
        if index >= 0:
            self.combo_mode.setCurrentIndex(index)

    def _conectar_sinais(self):
        """Conecta as alterações dos componentes diretamente às propriedades do settings."""
        self.checkbox_visibilidade.toggled.connect(
            lambda checked: setattr(settings, "side_panel_show_by_default", checked)
        )
        self.slider_width.valueChanged.connect(
            lambda value: setattr(settings, "side_panel_width", value)
        )
        self.combo_mode.currentIndexChanged.connect(
            lambda: setattr(settings, "side_panel_mode", self.combo_mode.currentData())
        )