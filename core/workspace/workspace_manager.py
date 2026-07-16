import logging
from typing import Optional
from core.workspace.contracts import IModule
from PySide6 import QtWidgets, QtCore
from .header_container.header_panel import HeaderPanel
from .toolbar_container.toolbar_manager import ToolbarManager
from .side_panel_container.side_panel_manager import SidePanelManager
from .layout import ModuleDistributor
from .registry import WorkspaceRegistry
from status_bar.status_bar import StatusBarManager
from .state import WorkspaceState

logger = logging.getLogger("OpenCMF.Workspace")

class WorkspaceManager(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = WorkspaceState()
        self.registry = WorkspaceRegistry()

        # 1. Setup da UI Base
        self.central_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # 2. Header (Topo absoluto)
        self.header = HeaderPanel()
        self.main_layout.addWidget(self.header)

        # 3. Gerenciadores de Layout (Toolbar)
        # Em vez de passar o layout para o manager, peça ao manager os containers e adicione-os aqui
        self.toolbar_manager = ToolbarManager()  # Ajuste o __init__ para não precisar do layout
        self.main_layout.addWidget(self.toolbar_manager.top_container)

        # 4. Área Central (Splitter)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.central_host = QtWidgets.QStackedWidget()
        self.splitter.addWidget(self.central_host)
        self.main_layout.addWidget(self.splitter, stretch=1)

        # 5. Toolbar Inferior (Adicione após a área central)
        self.main_layout.addWidget(self.toolbar_manager.bottom_container)

        # 6. SidePanel (Gerenciado pela QMainWindow, não pelo layout central)
        self.side_manager = SidePanelManager(self)

        # 7. StatusBar
        self.status_bar_manager = StatusBarManager()
        self.setStatusBar(self.status_bar_manager)

    def on_module_changed(self, module_id: str):
        try:
            ModuleDistributor.cleanup(
                self.toolbar_manager,
                self.side_manager,
                self.central_host
            )

            module = self.registry.get_or_create_module(module_id)

            ModuleDistributor.distribute(
                module,
                self.toolbar_manager,
                self.side_manager,
                self.central_host
            )

            logger.info(f"Módulo '{module_id}' carregado com sucesso.")
            self.status_bar_manager.showMessage(
                f"Módulo '{module_id}' carregado com sucesso.",
                3000
            )
        except Exception as e:
            logger.error(f"Erro crítico ao carregar módulo '{module_id}': {e}", exc_info=True)

            self.status_bar_manager.showMessage(f"Erro ao carregar módulo: {type(e).__name__}", 5000)

    def get_modulo_ativo(self) -> Optional[IModule]:
        """Retorna o módulo correspondente à aba atualmente selecionada."""
        current_index = self.header.tab_bar.currentIndex()
        if current_index >= 0:
            module_id = self.header.tab_bar.tabData(current_index)
            if module_id:
                return self.registry.get_or_create_module(module_id)
        return None

    def set_patient_path(self, path: str):
        """Atualiza o caminho do paciente no estado do workspace."""
        self.state.current_patient = path

    def reset_workspace(self):
        """Limpa o estado do workspace para um novo fluxo."""
        # Limpa o registro de módulos
        self.registry.clear_all()

        # Limpa o header (abas)
        self.header.clear_tabs()

        # Limpa toolbars através do gerenciador
        if hasattr(self, 'toolbar_manager'):
            self.toolbar_manager.clear_all()

        # Limpa os painéis laterais (opcional, mas recomendado)
        if hasattr(self, 'side_manager'):
            self.side_manager.clear_all()

        # Limpa o central_host
        self.central_host.setCurrentIndex(0)