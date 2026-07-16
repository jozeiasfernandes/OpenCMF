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

        # Splitter - Configuração crucial de política
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Central Host
        self.central_host = QtWidgets.QStackedWidget()
        # Garante que o central_host aceite expandir
        self.central_host.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.splitter.addWidget(self.central_host)

        # Side Manager
        self.side_manager = SidePanelManager(self)
        self.side_manager.container.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.splitter.addWidget(self.side_manager.container)

        # Configurações de comportamento do Splitter
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 1)

        # Adiciona o splitter ao layout com stretch=1 para consumir o espaço central
        self.main_layout.addWidget(self.splitter, stretch=1)

        # Toolbar Inferior e StatusBar
        self.main_layout.addWidget(self.toolbar_manager.bottom_container)

        self.status_bar_manager = StatusBarManager()
        self.main_layout.addWidget(self.status_bar_manager)

        # Ajuste de tamanho inicial
        QtCore.QTimer.singleShot(100, lambda: self.splitter.setSizes([900, 300]))

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
        self.registry.clear_all()
        self.header.clear_tabs()

        if hasattr(self, 'toolbar_manager'):
            self.toolbar_manager.clear_all()

        if hasattr(self, 'side_manager'):
            self.side_manager.clear_all()

        while self.central_host.count() > 0:
            widget = self.central_host.widget(0)
            self.central_host.removeWidget(widget)
            widget.deleteLater()