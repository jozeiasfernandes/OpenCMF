from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
from core.settings.localization.translator import tr


class SidePanelHeaderToolbox(QtWidgets.QWidget):
    """
    Cabeçalho específico para o Modo Toolbox do painel lateral,
    contendo o botão de alternância de gaveta, título e botão de configurações.
    """

    toggle_collapsed_changed = QtCore.Signal(bool)
    settings_requested = QtCore.Signal()

    def __init__(self, title_text: str = "Painel", workspace_manager=None, parent=None):
        super().__init__(parent)
        self.workspace_manager = workspace_manager
        self._collapsed = False

        # Define o diretório de assets com base na estrutura padrão (C:\OpenCMF\appearance\icons)
        self.assets_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "appearance" / "icons"
        self.icon_right_path = self.assets_dir / "arrow_right.svg"
        self.icon_left_path = self.assets_dir / "arrow_left.svg"

        self._setup_ui(title_text)

    def _setup_ui(self, title_text: str):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        self.btn_toggle = QtWidgets.QToolButton(self)
        self.btn_toggle.setStyleSheet("""
            QToolButton {
                border: none;
                background-colors: transparent;
            }
            QToolButton:hover {
                background-colors: rgba(255, 255, 255, 20);
                border-radius: 3px;
            }
        """)
        self.btn_toggle.setAutoRaise(True)
        self.btn_toggle.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_toggle.setToolTip(tr("side_panel.toggle", "Recolher / Expandir Painel Lateral"))

        self._update_toggle_icon(self._collapsed)
        self.btn_toggle.clicked.connect(self._toggle_state)
        layout.addWidget(self.btn_toggle)

        self.lbl_title = QtWidgets.QLabel(tr("side_panel.title", title_text), self)
        font = self.lbl_title.font()
        font.setBold(True)
        self.lbl_title.setFont(font)
        layout.addWidget(self.lbl_title)

        layout.addStretch()

        self.btn_config = QtWidgets.QToolButton(self)
        self.btn_config.setAutoRaise(True)
        self.btn_config.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_config.setToolTip(tr("side_panel.settings", "Configurações do Painel"))
        self.btn_config.setStyleSheet("""
            QToolButton {
                border: none;
                background-colors: transparent;
            }
            QToolButton:hover {
                background-colors: rgba(255, 255, 255, 20);
                border-radius: 3px;
            }
        """)

        config_icon_path = self.assets_dir / "config.svg"
        if config_icon_path.exists():
            pixmap = QtGui.QPixmap(str(config_icon_path))
            if not pixmap.isNull():
                self.btn_config.setIcon(
                    QtGui.QIcon(pixmap.scaled(14, 14, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                )

        self.btn_config.clicked.connect(self._open_settings)
        layout.addWidget(self.btn_config)

    def _update_toggle_icon(self, collapsed: bool):
        target_path = self.icon_left_path if collapsed else self.icon_right_path

        if target_path.exists():
            pixmap = QtGui.QPixmap(str(target_path))
            if not pixmap.isNull():
                self.btn_toggle.setIcon(
                    QtGui.QIcon(pixmap.scaled(14, 14, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)))
                return

        self.btn_toggle.setArrowType(QtCore.Qt.LeftArrow if collapsed else QtCore.Qt.RightArrow)

    def _toggle_state(self):
        self._collapsed = not self._collapsed
        self._update_toggle_icon(self._collapsed)

        if self._collapsed:
            self.lbl_title.hide()
            self.btn_config.hide()
        else:
            self.lbl_title.show()
            self.btn_config.show()

        self.toggle_collapsed_changed.emit(self._collapsed)

        if self.workspace_manager and hasattr(self.workspace_manager, "notificar_toggle_side_panel"):
            self.workspace_manager.toggle_side_panel_notification(self._collapsed)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self._toggle_state()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def _open_settings(self):
        self.settings_requested.emit()
        try:
            from core.settings.settings_dialog import SettingsDialog
            from settings.settings_page_tabs.workspace.tab_side_panel_settings import TabSidePanel
            dialog = SettingsDialog(workspace_manager=self.workspace_manager, parent=self)
            if hasattr(dialog, "selecionar_aba_por_tipo"):
                dialog.selecionar_aba_por_tipo(TabSidePanel)
            dialog.exec()
        except ImportError:
            from settings.settings_page_tabs.workspace.tab_side_panel_settings import TabSidePanel
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(tr("configs.side_panel", "Configurações do Side Panel"))
            dialog.resize(450, 300)
            lay = QtWidgets.QVBoxLayout(dialog)
            tab_widget = TabSidePanel(workspace_manager=self.workspace_manager)
            lay.addWidget(tab_widget)
            dialog.exec()

    def set_title(self, text: str):
        self.lbl_title.setText(text)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    header = SidePanelHeaderToolbox("Painel Toolbox")
    header.setWindowTitle("Teste SidePanelHeaderToolbox")
    header.resize(300, 50)
    header.show()

    sys.exit(app.exec())