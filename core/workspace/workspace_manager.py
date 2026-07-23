import logging
from typing import Any, Optional
from PySide6 import QtCore, QtWidgets

from core.workspace.containers.central_area_container.central_area_manager import CentralAreaManager
from core.workspace.containers.header_container.header_panel import HeaderPanel
from core.workspace.containers.header_container.workspace_modules import WorkspaceModulesMixin
from core.workspace.containers.side_panel_container.side_panel_manager import SidePanelManager
from core.workspace.containers.status_bar.status_bar import StatusBarManager
from core.workspace.containers.toolbar_container.toolbar_container import ToolbarContainer
from core.workspace.containers.toolbar_container.toolbar_manager import ToolbarManager

from core.workspace.models.registry import WorkspaceRegistry

from core.workspace.patient.state import WorkspaceState
from core.workspace.patient.workspace_patient import WorkspacePatientMixin

from core.workspace.services.workspace_loaders_components import WorkspaceComponentHandler

logger = logging.getLogger("OpenCMF.Workspace")


class WorkspaceManager(QtWidgets.QWidget, WorkspaceModulesMixin, WorkspacePatientMixin):
    """Gerencia o layout principal do workspace e a integração entre componentes."""

    MIN_CENTRAL_WIDTH = 200
    DEFAULT_STRETCH_FACTORS = [4, 1]

    def __init__(self, context: Optional[Any] = None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self.context = context
        self.state = WorkspaceState()
        self.registry = WorkspaceRegistry()

        self.current_patient_path = ""
        self.component_handler = WorkspaceComponentHandler(self)

        self._setup_layout()
        self._setup_components()
        self._configure_splitter()

    def _setup_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def _setup_components(self):
        self.header = HeaderPanel()
        self.main_layout.addWidget(self.header)

        self.toolbar_manager = ToolbarManager()
        self.main_layout.addWidget(self.toolbar_manager.top_container)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.central_manager = CentralAreaManager(self)
        self.splitter.addWidget(self.central_manager.get_container())

        self.side_manager = SidePanelManager(self)
        self.side_manager.container.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.splitter.addWidget(self.side_manager.container)

        self.main_layout.addWidget(self.splitter, stretch=1)
        self.main_layout.addWidget(self.toolbar_manager.bottom_container)

        self.status_bar_manager = StatusBarManager()
        self.main_layout.addWidget(self.status_bar_manager)

        # Protegido contra deleção prematura usando método separado e verificação
        QtCore.QTimer.singleShot(100, self._apply_initial_splitter_sizes)

    def _configure_splitter(self):
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, self.DEFAULT_STRETCH_FACTORS[0])
        self.splitter.setStretchFactor(1, self.DEFAULT_STRETCH_FACTORS[1])

    def _apply_initial_splitter_sizes(self):
        """Aplica os tamanhos iniciais do splitter de forma segura após o carregamento."""
        if not self.splitter or not self.splitter.isVisible():
            return
        self.splitter.setSizes([900, 300])

    def abrir_seletor_componentes(self):
        logger.info("Solicitação para abrir o seletor de componentes.")
        self.component_handler.abrir_seletor()

    def reset_workspace(self):
        logger.info("Iniciando o reset completo do workspace.")
        self.registry.clear_all()
        self.header.clear_tabs()
        self.toolbar_manager.clear_all()

        if hasattr(self.side_manager, 'clear_all'):
            self.side_manager.clear_all()

        self.central_manager.clear()
        logger.debug(f"Estado atual pós-reset - Módulos ativos: {self.registry.list_active_modules()}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    workspace = WorkspaceManager()
    workspace.setWindowTitle("Teste de WorkspaceManager")
    workspace.resize(1280, 720)

    workspace.show()

    sys.exit(app.exec())