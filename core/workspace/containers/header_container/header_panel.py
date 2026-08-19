from typing import Optional

from PySide6 import QtWidgets, QtCore

from core.workspace.containers.header_container.btn_home import HomeButton

# Settings
from core.settings.help.help_page import HelpPage
from settings.settings_page import PaginaConfig
from settings.icons.icon_manager import IconManager
from settings.settings_app_manager import settings


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

        # Conecta o sinal de mudança de tema de forma assíncrona assim como na Home_page
        QtCore.QTimer.singleShot(0, self._connect_theme_signal)

    def _setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        self.btn_home = HomeButton(QtCore.QSize(32, 32))
        self.btn_home.clicked_signal.connect(self.home_requested.emit)

        self.btn_loader_components = self._create_tool_button(
            "widgets", self._open_components_loader, "HeaderToolButton"
        )
        self.btn_help = self._create_tool_button(
            "help", self._open_help, "HeaderToolButton"
        )
        self.btn_settings = self._create_tool_button(
            "config", self._open_settings, "HeaderToolButton"
        )

        layout.addWidget(self.btn_home)
        # O layout customizado de abas do TabController será inserido dinamicamente aqui via add_tabs_layout()
        layout.addStretch(1)
        layout.addWidget(self.btn_loader_components)
        layout.addWidget(self.btn_help)
        layout.addWidget(self.btn_settings)

    def update_icons(self):
        """Atualiza dinamicamente as cores dos ícones do header com base no tema atual."""
        theme = settings.get("preferencias", "tema", "dark")
        manager = IconManager.get_instance()
        cor_default = manager.get_color(theme, "status", "default")

        # Atualiza os ícones utilitários usando o IconManager
        if hasattr(self, "btn_loader_components"):
            self.btn_loader_components.setIcon(manager.get_icon("widgets", color=cor_default, size=20))
        if hasattr(self, "btn_help"):
            self.btn_help.setIcon(manager.get_icon("help", color=cor_default, size=20))
        if hasattr(self, "btn_settings"):
            self.btn_settings.setIcon(manager.get_icon("config", color=cor_default, size=20))

    def _connect_theme_signal(self):
        """Conecta ao sinal de mudança de tema da janela principal se disponível."""
        if self.window() and hasattr(self.window(), 'theme_changed'):
            self.window().theme_changed.connect(self.update_icons)
            self.update_icons()
        else:
            QtCore.QTimer.singleShot(500, self._connect_theme_signal)

    def set_tab_bar(self, tab_bar: QtWidgets.QTabBar):
        """Substitui a QTabBar interna pela barra oficial gerenciada pelo TabController."""
        layout = self.layout()
        if layout and hasattr(self, 'tab_bar') and self.tab_bar:
            layout.replaceWidget(self.tab_bar, tab_bar)
            self.tab_bar.deleteLater()
            self.tab_bar = tab_bar
            self.tab_bar.currentChanged.connect(self._on_tab_changed)

    def _open_components_loader(self):
        """Delega a abertura do seletor de componentes diretamente ao workspace_manager se disponível."""
        if self.workspace_manager and hasattr(self.workspace_manager, "abrir_seletor_componentes"):
            self.workspace_manager.open_component_selector()
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
            self, icon_name: str, callback, object_name: str = ""
    ) -> QtWidgets.QToolButton:
        btn = QtWidgets.QToolButton()
        btn.setFixedSize(32, 32)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setAutoRaise(True)
        btn.setIconSize(QtCore.QSize(20, 20))

        if object_name:
            btn.setObjectName(object_name)

        btn.clicked.connect(callback)
        return btn

    def add_module_tab(self, module_id: str, title: str):
        if hasattr(self, 'tab_bar') and self.tab_bar:
            index = self.tab_bar.addTab(title)
            self.tab_bar.setTabData(index, module_id)

    def clear_tabs(self):
        if hasattr(self, 'tab_bar') and self.tab_bar:
            while self.tab_bar.count() > 0:
                self.tab_bar.removeTab(0)

    def add_tabs_layout(self, tabs_layout: QtWidgets.QHBoxLayout):
        """Insere o layout customizado de abas do TabController logo após o botão Home."""
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(2)

        # Insere na posição correta (após o btn_home, que é o índice 0)
        self.layout().insertLayout(1, tabs_layout)


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