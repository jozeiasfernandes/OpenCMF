from PySide6 import QtWidgets, QtCore, QtGui
from core import tr

class SidePanelHeader(QtWidgets.QWidget):
    """Cabeçalho personalizado para o painel lateral com título, botão de recolher e botão de configurações."""

    toggle_colapsado_alterado = QtCore.Signal(bool)
    configuracoes_solicitadas = QtCore.Signal()

    def __init__(self, titulo: str = "Side Panel", workspace_manager=None, parent=None):
        super().__init__(parent)
        self.workspace_manager = workspace_manager
        self._colapsado = False
        self._setup_ui(titulo)

    def _setup_ui(self, titulo_texto: str):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)
        self.btn_toggle = QtWidgets.QToolButton(self)
        self.btn_toggle.setArrowType(QtCore.Qt.DownArrow)
        self.btn_toggle.setAutoRaise(True)
        self.btn_toggle.setToolTip(tr("side_panel.toggle", "Recolher / Expandir Painel"))
        self.btn_toggle.clicked.connect(self._alternar_estado)
        layout.addWidget(self.btn_toggle)
        self.lbl_titulo = QtWidgets.QLabel(tr("side_panel.title", titulo_texto), self)
        font = self.lbl_titulo.font()
        font.setBold(True)
        self.lbl_titulo.setFont(font)
        layout.addWidget(self.lbl_titulo)
        layout.addStretch()
        self.btn_config = QtWidgets.QToolButton(self)
        self.btn_config.setText("⚙")
        self.btn_config.setAutoRaise(True)
        self.btn_config.setToolTip(tr("side_panel.settings", "Configurações do Painel"))
        self.btn_config.clicked.connect(self._abrir_configuracoes)
        layout.addWidget(self.btn_config)

    def _alternar_estado(self):
        self._colapsado = not self._colapsado
        if self._colapsado:
            self.btn_toggle.setArrowType(QtCore.Qt.RightArrow)
        else:
            self.btn_toggle.setArrowType(QtCore.Qt.DownArrow)

        self.toggle_colapsado_alterado.emit(self._colapsado)

    def _abrir_configuracoes(self):
        """Abre a janela de configurações focada na aba do Side Panel passando o workspace_manager."""
        self.configuracoes_solicitadas.emit()
        try:
            from core.settings.settings_dialog import SettingsDialog
            from core.settings.tabs.workspace.tab_side_panel_settings import TabSidePanel
            dialog = SettingsDialog(workspace_manager=self.workspace_manager, parent=self)
            if hasattr(dialog, "selecionar_aba_por_tipo"):
                dialog.selecionar_aba_por_tipo(TabSidePanel)
            dialog.exec()
        except ImportError:
            from core.settings.tabs.workspace.tab_side_panel_settings import TabSidePanel
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(tr("configs.side_panel", "Configurações do Side Panel"))
            dialog.resize(450, 300)
            lay = QtWidgets.QVBoxLayout(dialog)
            tab_widget = TabSidePanel(workspace_manager=self.workspace_manager)
            lay.addWidget(tab_widget)

            dialog.exec()

    def set_titulo(self, texto: str):
        self.lbl_titulo.setText(texto)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    widget = SidePanelHeader("Side Panel")
    widget.setWindowTitle("Teste SidePanelHeader")
    widget.resize(300, 50)
    widget.show()

    sys.exit(app.exec())