from typing import Optional
from core.workspace.contracts import IModule
from PySide6 import QtWidgets, QtCore
from .header_container.header_panel import HeaderPanel
from .toolbar_container.toolbar_manager import ToolbarManager
from .side_panel_container.side_panel_manager import SidePanelManager
from .layout import ModuleDistributor
from .registry import WorkspaceRegistry
from .components.status_bar import StatusBarManager


class WorkspaceManager(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.registry = WorkspaceRegistry()

        # 1. Setup da UI Base
        self.central_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # 2. Header
        self.header = HeaderPanel()
        self.main_layout.addWidget(self.header)

        # 3. Gerenciadores de Layout
        self.toolbar_manager = ToolbarManager(self.main_layout)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.central_host = QtWidgets.QStackedWidget()
        self.splitter.addWidget(self.central_host)
        self.main_layout.addWidget(self.splitter, stretch=1)

        self.side_manager = SidePanelManager(self)

        # 4. StatusBar
        self.status_bar_manager = StatusBarManager()
        self.setStatusBar(self.status_bar_manager)

        # 5. Conexões únicas
        self.header.module_changed.connect(self.on_module_changed)

    def on_module_changed(self, module_id: str):
        try:
            # 1. Limpeza do estado anterior
            ModuleDistributor.cleanup(self.toolbar_manager, self.side_manager, self.central_host)

            # 2. Instanciação ou recuperação do novo módulo
            module = self.registry.get_or_create_module(module_id)

            # 3. Injeção visual
            ModuleDistributor.distribute(module, self.toolbar_manager, self.side_manager, self.central_host)

            # 4. Feedback ao usuário
            self.status_bar_manager.show_message(f"Módulo '{module_id}' carregado com sucesso.", 3000)

        except Exception as e:
            self.status_bar_manager.show_message(f"Erro ao carregar módulo: {str(e)}")
            print(f"Erro crítico no WorkspaceManager: {e}")

    def get_modulo_ativo(self) -> Optional[IModule]:
        """Retorna o módulo correspondente à aba atualmente selecionada."""
        current_index = self.header.tab_bar.currentIndex()
        if current_index >= 0:
            module_id = self.header.tab_bar.tabData(current_index)
            if module_id:
                return self.registry.get_or_create_module(module_id)
        return None