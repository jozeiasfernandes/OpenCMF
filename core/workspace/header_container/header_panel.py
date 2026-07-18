from pathlib import Path
from typing import Optional

from PySide6 import QtWidgets, QtCore, QtGui
from core.workspace.btn_home import HomeButton
from core.loaders.components_list import Components_List


class HeaderPanel(QtWidgets.QWidget):
    """Barra de cabeçalho do workspace com botão Home, abas e configurações."""

    home_requested = QtCore.Signal()
    settings_requested = QtCore.Signal()
    module_changed = QtCore.Signal(str)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self.setFixedHeight(42)

        self.base_dir = Path(__file__).resolve().parents[3]

        self._setup_ui()

    def _setup_ui(self):
        """Configura o layout e os widgets do header."""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # Botão Home
        self.btn_home = HomeButton(self.base_dir, QtCore.QSize(32, 32))
        self.btn_home.clicked_signal.connect(self.home_requested.emit)

        # Barra de abas
        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.setDrawBase(False)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setMovable(True)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        # Defina o caminho do ícone aqui para garantir que esteja correto
        config_icon_path = self.base_dir / "appearance" / "icons" / "config_branco.svg"

        # Botão de configurações passando o caminho do ícone
        self.btn_config = self._create_tool_button(
            "config_branco",
            self._open_components_loader,
            icon_path=config_icon_path
        )

        # Montagem do layout
        layout.addWidget(self.btn_home)
        layout.addWidget(self.tab_bar)
        layout.addStretch(1)
        layout.addWidget(self.btn_config)

    def _open_components_loader(self):
        """Abre a janela de carregamento de componentes de forma segura."""
        try:
            loader_dialog = Components_List(parent=self)
            loader_dialog.exec()
        except ImportError as e:
            print(f"Erro ao importar Components_List: {e}")
        except Exception as e:
            print(f"Erro ao abrir o gerenciador de componentes: {e}")

    def _create_tool_button(
            self, icon_name: str, callback, icon_path: Optional[Path] = None
    ) -> QtWidgets.QToolButton:
        btn = QtWidgets.QToolButton()
        btn.setFixedSize(32, 32)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setAutoRaise(True)

        # Se um caminho de ícone for fornecido, usa ele
        if icon_path and icon_path.exists():
            btn.setIcon(QtGui.QIcon(str(icon_path)))
            btn.setIconSize(QtCore.QSize(24, 24))
        else:
            # Caso contrário, mantém o texto como fallback
            btn.setText(icon_name[0].upper())

        btn.clicked.connect(callback)
        return btn

    def _on_tab_changed(self, index: int):
        """Emite sinal quando a aba ativa é alterada."""
        if index >= 0:
            module_id = self.tab_bar.tabData(index)
            if module_id:
                self.module_changed.emit(module_id)

    def add_module_tab(self, module_id: str, title: str):
        """Adiciona uma nova aba de módulo."""
        index = self.tab_bar.addTab(title)
        self.tab_bar.setTabData(index, module_id)

    def clear_tabs(self):
        """Remove todas as abas."""
        while self.tab_bar.count() > 0:
            self.tab_bar.removeTab(0)


# ======================= Teste isolado =======================
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    header = HeaderPanel()

    # Dados de teste
    header.add_module_tab("mod_1", "Análise 3D")
    header.add_module_tab("mod_2", "Relatórios")

    # Conexões para debug
    header.home_requested.connect(lambda: print("Home solicitada"))
    header.settings_requested.connect(lambda: print("Configurações solicitadas"))
    header.module_changed.connect(lambda mid: print(f"Módulo alterado para: {mid}"))

    header.show()
    sys.exit(app.exec())