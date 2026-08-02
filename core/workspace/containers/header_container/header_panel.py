from pathlib import Path
from typing import Optional

from PySide6 import QtWidgets, QtCore, QtGui

from core.workspace.containers.header_container.btn_home import HomeButton

# Settings
from list_paths import ICONS_DIR
from core.settings.help.help_page import HelpPage
from settings.settings_page import PaginaConfig




class HeaderPanel(QtWidgets.QWidget):
    """Barra de cabeçalho do workspace com botão Home, abas e janelas flutuantes."""

    home_requested = QtCore.Signal()
    module_changed = QtCore.Signal(str)
    components_loader_requested = QtCore.Signal()

    def __init__(self, workspace_manager=None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.workspace_manager = workspace_manager

        self.setFixedHeight(42)

        # Inicializa referências para evitar lixo de memória e erros de acesso
        self.help_win = None
        self.settings_win = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        self.btn_home = HomeButton(QtCore.QSize(32, 32))
        self.btn_home.clicked_signal.connect(self.home_requested.emit)

        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.setDrawBase(False)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setMovable(True)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        self.btn_loader_components = self._create_tool_button(
            "widgets", self._open_components_loader, ICONS_DIR / "widgets.svg"
        )
        self.btn_help = self._create_tool_button(
            "help", self._open_help, ICONS_DIR / "help.svg"
        )
        self.btn_settings = self._create_tool_button(
            "settings", self._open_settings, ICONS_DIR / "config.svg"
        )

        layout.addWidget(self.btn_home)
        layout.addWidget(self.tab_bar)
        layout.addStretch(1)
        layout.addWidget(self.btn_loader_components)
        layout.addWidget(self.btn_help)
        layout.addWidget(self.btn_settings)

    def _open_components_loader(self):
        """Delega a abertura do seletor de componentes diretamente ao workspace_manager se disponível."""
        if self.workspace_manager and hasattr(self.workspace_manager, "abrir_seletor_componentes"):
            self.workspace_manager.abrir_seletor_componentes()
        else:
            self.components_loader_requested.emit()

    def _open_help(self):
        """Abre a página de ajuda como janela isolada."""
        self.help_win = HelpPage(parent=self)
        self.help_win.setWindowFlags(QtCore.Qt.Window)
        self.help_win.show()

    def _open_settings(self):
        """Abre a página de configurações como janela isolada."""
        self.settings_win = PaginaConfig(parent=self)
        self.settings_win.setWindowFlags(QtCore.Qt.Window)
        self.settings_win.show()

    def _create_tool_button(
            self, icon_name: str, callback, icon_path: Optional[Path] = None
    ) -> QtWidgets.QToolButton:
        btn = QtWidgets.QToolButton()
        btn.setFixedSize(32, 32)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setAutoRaise(True)

        if icon_path and icon_path.exists():
            btn.setIcon(QtGui.QIcon(str(icon_path)))
            btn.setIconSize(QtCore.QSize(24, 24))
        else:
            btn.setText(icon_name[0].upper())

        btn.clicked.connect(callback)
        return btn

    def _on_tab_changed(self, index: int):
        if index >= 0:
            module_id = self.tab_bar.tabData(index)
            if module_id:
                self.module_changed.emit(module_id)

    def add_module_tab(self, module_id: str, title: str):
        index = self.tab_bar.addTab(title)
        self.tab_bar.setTabData(index, module_id)

    def clear_tabs(self):
        while self.tab_bar.count() > 0:
            self.tab_bar.removeTab(0)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    header = HeaderPanel()
    header.add_module_tab("mod_1", "Análise 3D")
    header.add_module_tab("mod_2", "Relatórios")

    header.home_requested.connect(lambda: print("Home solicitada"))
    header.module_changed.connect(lambda mid: print(f"Módulo alterado para: {mid}"))
    header.components_loader_requested.connect(lambda: print("Loader de componentes solicitado"))

    header.show()
    sys.exit(app.exec())