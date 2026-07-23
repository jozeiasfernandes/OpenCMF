from pathlib import Path
from typing import Optional

from PySide6 import QtWidgets, QtCore, QtGui
from core.workspace.containers.header_container.btn_home import HomeButton
from core.loaders.components_list import Components_List
from core.settings.help.help_page import HelpPage
from core.settings.settings_page import PaginaConfig


class HeaderPanel(QtWidgets.QWidget):
    """Barra de cabeçalho do workspace com botão Home, abas e janelas flutuantes."""

    home_requested = QtCore.Signal()
    module_changed = QtCore.Signal(str)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self.setFixedHeight(42)
        self.base_dir = Path(__file__).resolve().parents[4]

        # Inicializa referências para evitar lixo de memória e erros de acesso
        self.help_win = None
        self.settings_win = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        self.btn_home = HomeButton(self.base_dir, QtCore.QSize(32, 32))
        self.btn_home.clicked_signal.connect(self.home_requested.emit)

        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.setDrawBase(False)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setMovable(True)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        icons_dir = self.base_dir / "appearance" / "icons"

        self.btn_loader_components = self._create_tool_button(
            "widgets", self._open_components_loader, icons_dir / "widgets.svg"
        )
        self.btn_help = self._create_tool_button(
            "help", self._open_help, icons_dir / "help.svg"
        )
        self.btn_settings = self._create_tool_button(
            "settings", self._open_settings, icons_dir / "config.svg"
        )

        layout.addWidget(self.btn_home)
        layout.addWidget(self.tab_bar)
        layout.addStretch(1)
        layout.addWidget(self.btn_loader_components)
        layout.addWidget(self.btn_help)
        layout.addWidget(self.btn_settings)

    def _open_components_loader(self):
        try:
            loader_dialog = Components_List(parent=self)
            loader_dialog.exec()
        except Exception as e:
            print(f"Erro ao abrir o gerenciador de componentes: {e}")

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

    # O HeaderPanel agora gerencia suas próprias janelas de config e ajuda
    header = HeaderPanel()

    # Dados de teste
    header.add_module_tab("mod_1", "Análise 3D")
    header.add_module_tab("mod_2", "Relatórios")

    # Conexões para debug
    header.home_requested.connect(lambda: print("Home solicitada"))
    header.module_changed.connect(lambda mid: print(f"Módulo alterado para: {mid}"))

    header.show()
    sys.exit(app.exec())