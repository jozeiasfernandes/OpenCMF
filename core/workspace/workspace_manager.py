from PySide6 import QtWidgets, QtCore
import logging

from core.workspace.header_container.header_panel import HeaderPanel
from core.workspace.toolbar_container.toolbar_manager import ToolbarManager
from core.workspace.side_panel_container.side_panel_manager import SidePanelManager
from core.workspace.central_area_container.central_area_manager import CentralAreaManager
from core.workspace.status_bar.status_bar import StatusBarManager
from core.workspace.state import WorkspaceState
from core.workspace.registry import WorkspaceRegistry
from core.workspace.workspace_loaders_components import WorkspaceComponentHandler


from core.workspace.workspace_modules import WorkspaceModulesMixin
from core.workspace.workspace_patient import WorkspacePatientMixin

logger = logging.getLogger("OpenCMF.Workspace")

class WorkspaceManager(QtWidgets.QWidget, WorkspaceModulesMixin, WorkspacePatientMixin):
    """Gerencia o layout principal do workspace e a integração entre componentes."""

    MIN_CENTRAL_WIDTH = 200
    DEFAULT_STRETCH_FACTORS = [4, 1]

    def __init__(self, parent=None):
        super().__init__(parent)

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

        QtCore.QTimer.singleShot(100, lambda: self.splitter.setSizes([900, 300]))

    def _configure_splitter(self):
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 1)

    def abrir_seletor_componentes(self):
        self.component_handler.abrir_seletor()

    def reset_workspace(self):
        self.registry.clear_all()
        self.header.clear_tabs()
        self.toolbar_manager.clear_all()

        if hasattr(self.side_manager, 'clear_all'):
            self.side_manager.clear_all()
        elif hasattr(self.side_manager.container, 'clear_all'):
            self.side_manager.container.clear_all()

        self.central_manager.clear()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    workspace = WorkspaceManager()
    workspace.setWindowTitle("Teste de WorkspaceManager")
    workspace.resize(1280, 720)

    workspace.show()

    sys.exit(app.exec())