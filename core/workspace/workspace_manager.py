import logging
from typing import Optional
from core.workspace.contracts import IModule
from PySide6 import QtWidgets, QtCore
from .header_container.header_panel import HeaderPanel
from .toolbar_container.toolbar_manager import ToolbarManager
from .side_panel_container.side_panel_manager import SidePanelManager
from .central_area_container.central_area_manager import CentralAreaManager
from .layout import ModuleDistributor
from .registry import WorkspaceRegistry
from status_bar.status_bar import StatusBarManager
from .state import WorkspaceState


logger = logging.getLogger("OpenCMF.Workspace")


class WorkspaceManager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = WorkspaceState()
        self.registry = WorkspaceRegistry()

        # Layout Principal
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header e Toolbar
        self.header = HeaderPanel()
        self.main_layout.addWidget(self.header)

        self.toolbar_manager = ToolbarManager()
        self.main_layout.addWidget(self.toolbar_manager.top_container)

        # Splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Central Manager (Substitui o QStackedWidget)
        self.central_manager = CentralAreaManager(self)
        self.splitter.addWidget(self.central_manager.get_container())

        # Side Manager
        self.side_manager = SidePanelManager(self)
        self.side_manager.container.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.splitter.addWidget(self.side_manager.container)

        # Configurações do Splitter
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 1)
        self.main_layout.addWidget(self.splitter, stretch=1)

        # Toolbar Inferior e StatusBar
        self.main_layout.addWidget(self.toolbar_manager.bottom_container)
        self.status_bar_manager = StatusBarManager()
        self.main_layout.addWidget(self.status_bar_manager)

        QtCore.QTimer.singleShot(100, lambda: self.splitter.setSizes([900, 300]))

    def on_module_changed(self, module_id: str):
        try:
            # Passamos o central_manager em vez do central_host
            ModuleDistributor.cleanup(
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            module = self.registry.get_or_create_module(module_id)

            ModuleDistributor.distribute(
                module,
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            logger.info(f"Módulo '{module_id}' carregado com sucesso.")
            self.status_bar_manager.showMessage(f"Módulo '{module_id}' carregado.", 3000)
        except Exception as e:
            logger.error(f"Erro crítico: {e}", exc_info=True)
            self.status_bar_manager.showMessage("Erro ao carregar módulo", 5000)

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
        self.registry.clear_all()
        self.header.clear_tabs()
        self.toolbar_manager.clear_all()
        self.side_manager.clear_all()
        self.central_manager.clear()