from PySide6 import QtWidgets, QtCore
from core.settings.localization.translator import tr
from core.settings.settings_app_manager import settings


class TabSidePanel(QtWidgets.QWidget):
    """Aba de configurações para o Side Panel com atualização em tempo real."""

    def __init__(self, workspace_manager=None):
        super().__init__()
        self.workspace_manager = workspace_manager
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

        # Configuração do modo de exibição / estilo de container (Tab Widget vs Toolbox vs Floating)
        mode_layout = QtWidgets.QHBoxLayout()
        self.lbl_mode = QtWidgets.QLabel(tr("configs.side_panel.mode", "Modo do Container:"))
        self.combo_mode = QtWidgets.QComboBox()
        self.combo_mode.addItem(tr("configs.side_panel.mode.tabs", "Abas Laterais (East)"), "tabs")
        self.combo_mode.addItem(tr("configs.side_panel.mode.toolbox", "Painéis Empilhados (Toolbox / Colapsável)"),
                                "toolbox")
        self.combo_mode.addItem(tr("configs.side_panel.mode.floating", "Painel Flutuante (Floating)"),
                                "floating")
        mode_layout.addWidget(self.lbl_mode)
        mode_layout.addWidget(self.combo_mode)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        layout.addStretch()

    def _carregar_valores(self):
        """Carrega os valores salvos no settings_manager para os widgets sem disparar sinais acidentais."""
        self.checkbox_visibilidade.blockSignals(True)
        self.combo_mode.blockSignals(True)

        self.checkbox_visibilidade.setChecked(settings.side_panel_show_by_default)

        index = self.combo_mode.findData(settings.side_panel_mode)
        if index >= 0:
            self.combo_mode.setCurrentIndex(index)

        self.checkbox_visibilidade.blockSignals(False)
        self.combo_mode.blockSignals(False)

    def _conectar_sinais(self):
        """Conecta as alterações salvando e atualizando o workspace em tempo real."""
        self.checkbox_visibilidade.toggled.connect(self._atualizar_visibilidade)
        self.combo_mode.currentIndexChanged.connect(self._atualizar_modo)

    def _atualizar_visibilidade(self, checked: bool):
        settings.side_panel_show_by_default = checked
        if self.workspace_manager and hasattr(self.workspace_manager, "side_manager"):
            side_manager = self.workspace_manager.side_manager
            current_mode = getattr(settings, "side_panel_mode", "toolbox")

            if current_mode == "floating":
                # No modo flutuante, atualiza a visibilidade da janela flutuante em vez do container embutido
                if hasattr(side_manager.container, "floating_window") and side_manager.container.floating_window:
                    if checked:
                        side_manager.container.floating_window.show()
                    else:
                        side_manager.container.floating_window.hide()
            else:
                if hasattr(side_manager, "container") and side_manager.container:
                    side_manager.container.setVisible(checked)

    def _atualizar_modo(self):
        mode = self.combo_mode.currentData()
        if mode is not None:
            settings.side_panel_mode = mode
            if self.workspace_manager and hasattr(self.workspace_manager, "reconstruir_side_panel"):
                self.workspace_manager.reconstruir_side_panel()