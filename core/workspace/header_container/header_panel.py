from pathlib import Path
from typing import Optional

from PySide6 import QtWidgets, QtCore, QtGui

from core.workspace.btn_home import HomeButton


class HeaderPanel(QtWidgets.QWidget):
    home_requested = QtCore.Signal()
    settings_requested = QtCore.Signal()
    module_changed = QtCore.Signal(str)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(42)

        # Define o diretório base do projeto para localizar ícones
        self.base_dir = Path(__file__).resolve().parents[2]

        self._setup_ui()

    def _setup_ui(self):
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

        # Botão de configurações
        self.btn_config = self._create_tool_button("settings", self.settings_requested.emit)

        # Montagem do layout
        layout.addWidget(self.btn_home)
        layout.addWidget(self.tab_bar)
        layout.addStretch(1)
        layout.addWidget(self.btn_config)

    def _create_tool_button(
        self, icon_name: str, callback
    ) -> QtWidgets.QToolButton:
        btn = QtWidgets.QToolButton()
        btn.setFixedSize(32, 32)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setAutoRaise(True)
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


# Bloco de teste isolado
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # Cria o painel
    header = HeaderPanel()

    # Adiciona alguns dados para teste
    header.add_module_tab("mod_1", "Análise 3D")
    header.add_module_tab("mod_2", "Relatórios")

    # Conecta sinais para debug no console
    header.home_requested.connect(lambda: print("Home solicitada"))
    header.settings_requested.connect(lambda: print("Configurações solicitadas"))
    header.module_changed.connect(lambda mid: print(f"Módulo alterado para: {mid}"))

    header.show()
    sys.exit(app.exec())