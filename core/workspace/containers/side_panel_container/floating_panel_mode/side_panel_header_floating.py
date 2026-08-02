from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
from core.settings.localization.translator import tr


class SidePanelHeaderFloating(QtWidgets.QWidget):
    """
    Cabeçalho específico para o Modo Floating / Toolbox Flutuante,
    contendo botões para alternar, reanexar ou fechar o painel.
    """

    toggle_collapsed_changed = QtCore.Signal(bool)
    settings_requested = QtCore.Signal()
    dock_requested = QtCore.Signal()

    def __init__(self, title_text: str = "Painel Flutuante", workspace_manager=None, parent=None):
        super().__init__(parent)
        self.workspace_manager = workspace_manager
        self._collapsed = False

        # Define o diretório de assets com base na estrutura padrão (C:\OpenCMF\appearance\icons)
        self.assets_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "appearance" / "icons"
        self.icon_up_path = self.assets_dir / "arrow_up.svg"
        self.icon_down_path = self.assets_dir / "arrow_down.svg"

        self._setup_ui(title_text)

    def _setup_ui(self, title_text: str):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        self.btn_toggle = QtWidgets.QToolButton(self)
        self.btn_toggle.setStyleSheet("""
            QToolButton {
                border: none;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 3px;
            }
        """)
        self.btn_toggle.setAutoRaise(True)
        self.btn_toggle.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_toggle.setToolTip(tr("side_panel.toggle", "Recolher / Expandir Painel Flutuante"))

        self._update_toggle_icon(self._collapsed)
        self.btn_toggle.clicked.connect(self._toggle_state)
        layout.addWidget(self.btn_toggle)

        self.lbl_title = QtWidgets.QLabel(tr("side_panel.title", title_text), self)
        font = self.lbl_title.font()
        font.setBold(True)
        self.lbl_title.setFont(font)
        layout.addWidget(self.lbl_title)

        layout.addStretch()

        # Botão para reanexar à workspace
        self.btn_dock = QtWidgets.QToolButton(self)
        self.btn_dock.setAutoRaise(True)
        self.btn_dock.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_dock.setToolTip(tr("side_panel.dock", "Reanexar à Workspace"))
        self.btn_dock.setStyleSheet("""
            QToolButton {
                border: none;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 3px;
            }
        """)

        dock_icon_path = self.assets_dir / "arrow_circle_right.svg"
        if dock_icon_path.exists():
            pixmap_dock = QtGui.QPixmap(str(dock_icon_path))
            if not pixmap_dock.isNull():
                self.btn_dock.setIcon(
                    QtGui.QIcon(pixmap_dock.scaled(14, 14, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                )
            else:
                self.btn_dock.setText("➔")
        else:
            self.btn_dock.setText("➔")

        self.btn_dock.clicked.connect(self.dock_requested.emit)
        layout.addWidget(self.btn_dock)

        # Botão de Configurações
        self.btn_config = QtWidgets.QToolButton(self)
        self.btn_config.setAutoRaise(True)
        self.btn_config.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_config.setToolTip(tr("side_panel.settings", "Configurações do Painel"))
        self.btn_config.setStyleSheet("""
            QToolButton {
                border: none;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 3px;
            }
        """)

        config_icon_path = self.assets_dir / "config.svg"
        if config_icon_path.exists():
            pixmap_config = QtGui.QPixmap(str(config_icon_path))
            if not pixmap_config.isNull():
                self.btn_config.setIcon(
                    QtGui.QIcon(pixmap_config.scaled(14, 14, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                )

        self.btn_config.clicked.connect(self._open_settings)
        layout.addWidget(self.btn_config)

    def _update_toggle_icon(self, collapsed: bool):
        target_path = self.icon_down_path if collapsed else self.icon_up_path

        if target_path.exists():
            pixmap = QtGui.QPixmap(str(target_path))
            if not pixmap.isNull():
                self.btn_toggle.setIcon(
                    QtGui.QIcon(pixmap.scaled(14, 14, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)))
                return

        self.btn_toggle.setArrowType(QtCore.Qt.DownArrow if collapsed else QtCore.Qt.UpArrow)

    def _toggle_state(self):
        self._collapsed = not self._collapsed
        self._update_toggle_icon(self._collapsed)

        self.toggle_collapsed_changed.emit(self._collapsed)

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

    header = SidePanelHeaderFloating("Painel Flutuante")
    header.setWindowTitle("Teste SidePanelHeaderFloating")
    header.resize(300, 50)
    header.show()

    sys.exit(app.exec())