import logging
from typing import Any, Optional

from PySide6 import QtCore, QtWidgets

# Patient
from application.patient.patient_manager import PatientManager
from core.application.patient.patient_config_manager import PatientConfigManager
from settings.paths.list_paths import PATIENTS_DIR
from core.workspace.patient.workspace_patient import WorkspacePatientMixin
from core.workspace.patient.state import WorkspaceState

# Project
from project_manager.project_service import ProjectServiceHomePage

# Settings
from settings.settings_app_manager import settings

# Logs
from core.settings.logs.archives.workspace_log import Workspace_Logger
from settings.logs.archives.containers import container
logger = logging.getLogger("OpenCMF.Workspace")

# Workspace
from core.workspace.models.registry import WorkspaceRegistry

# Module
from core.workspace.modules.module_manager import WorkspaceModuleManager

# Loader Components
from core.workspace.layout.loaders_components import WorkspaceComponentHandler

# Containers
from core.workspace.containers.header_container.header_panel import HeaderPanel
from core.workspace.containers.toolbar_container.toolbar_manager import ToolbarManager
from core.workspace.containers.central_area_container.central_area_manager import CentralAreaManager
from core.workspace.containers.side_panel_container.side_panel_container import SidePanelContainer
from core.workspace.containers.side_panel_container.side_panel_manager import SidePanelManager
from core.workspace.containers.status_bar.status_bar import StatusBarManager


class WorkspaceManager(QtWidgets.QWidget, WorkspacePatientMixin):
    """Gerencia o layout principal do workspace e a integração entre componentes."""

    MIN_CENTRAL_WIDTH = 200
    DEFAULT_STRETCH_FACTORS = [4, 1]

    def __init__(self, context: Optional[Any] = None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        containers_logger = container.containers_logger()
        state_info = containers_logger.inspect_container_state(container)
        containers_logger.info(
            f"Container inspecionado via Workspace. Provedores ativos: {state_info.get('providers', [])}",
            container_name="ApplicationContainer"
        )

        self.context = context
        self.state = WorkspaceState()
        self.registry = WorkspaceRegistry()

        # Integração com o PatientManager via contexto injetado (ou fallback seguro)
        self.project_service = ProjectServiceHomePage(PATIENTS_DIR)

        if self.context and hasattr(self.context, 'patient_manager') and self.context.patient_manager:
            self.patient_manager = self.context.patient_manager
        else:
            self.config_manager = PatientConfigManager()
            self.patient_manager = PatientManager(config_manager=self.config_manager)

        # Sincroniza o path inicial do paciente ativo se houver (usando a propriedade correta .current_path)
        self.current_patient_path = self.patient_manager.current_path or ""

        self.component_handler = WorkspaceComponentHandler(self)

        # Instancia o logger/inspetor passando a referência do workspace
        self.debug_inspector = Workspace_Logger(self)

        self._setup_layout()
        self._setup_components()
        self._configure_splitter()

    # =====================================================================
    # INITIAL CONFIGURATION AND LAYOUT
    # =====================================================================

    def _setup_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def _setup_components(self):
        # 1. Instancia os gerenciadores e a área central primeiro para que o tab_controller/tab_bar existam
        self.central_manager = CentralAreaManager(self)

        self.toolbar_manager = ToolbarManager()

        self.module_manager = WorkspaceModuleManager(
            container=self.central_manager.get_container(),
            registry=self.registry,
            toolbar_manager=self.toolbar_manager,
            side_manager=None,  # Será associado logo abaixo
            central_manager=self.central_manager,
            parent=self
        )

        # 2. Instancia o HeaderPanel e injeta o tab_bar_layout oficial gerido pelo WorkspaceModuleManager
        self.header = HeaderPanel(workspace_manager=self)
        if hasattr(self.module_manager, "tab_controller") and hasattr(self.module_manager.tab_controller, "tab_bar_layout"):
            if hasattr(self.header, "add_tabs_layout"):
                self.header.add_tabs_layout(self.module_manager.tab_controller.tab_bar_layout)
            elif hasattr(self.header, "set_tab_bar"):
                self.header.set_tab_bar(self.module_manager.tab_controller.tab_bar_layout)

        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.toolbar_manager.top_container)

        # 3. Inicializa o QSplitter antes de adicionar componentes dependentes dele
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Adiciona a área central (ficará à esquerda)
        self.splitter.addWidget(self.central_manager.get_container())

        # 4. Instancia o gerenciador do painel lateral
        self.side_manager = SidePanelManager(self)
        self.module_manager.side_manager = self.side_manager

        if hasattr(self.side_manager, "container") and self.side_manager.container:
            if hasattr(self.side_manager.container, "toggle_requested"):
                self.side_manager.container.toggle_requested.connect(self.toggle_side_panel_notification)

        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")
        if current_mode != "floating":
            self.side_manager.container.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            self.splitter.addWidget(self.side_manager.container)
            self.splitter.setStretchFactor(0, 7)
            self.splitter.setStretchFactor(1, 3)
        else:
            self.splitter.setStretchFactor(0, 1)

        self.main_layout.addWidget(self.splitter, stretch=1)
        self.main_layout.addWidget(self.toolbar_manager.bottom_container)

        self.status_bar_manager = StatusBarManager()
        self.module_manager.status_bar_manager = self.status_bar_manager
        self.main_layout.addWidget(self.status_bar_manager)

        try:
            containers_logger = container.containers_logger()
            if hasattr(self.side_manager, "container") and self.side_manager.container:
                containers_logger.inspect_side_panel_widgets(self.side_manager.container, container_name="SidePanelDiagnostic")
        except Exception as e:
            logger.error(f"Erro ao rodar diagnóstico do side panel: {e}")

    def showEvent(self, event):
        super().showEvent(event)
        QtCore.QTimer.singleShot(50, self._apply_initial_splitter_sizes)

    # =====================================================================
    # SIDE PANEL AND SPLITTER MANAGEMENT
    # =====================================================================

    def _configure_splitter(self):
        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")

        if current_mode == "floating":
            self.splitter.setCollapsible(0, False)
            self.splitter.setStretchFactor(0, 1)
            return

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)
        self.splitter.setChildrenCollapsible(True)

        self.splitter.setStretchFactor(0, 7)
        self.splitter.setStretchFactor(1, 3)

    def _apply_initial_splitter_sizes(self):
        if not self.splitter or not self.splitter.isVisible():
            return

        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")
        if current_mode == "floating":
            self.splitter.setSizes([self.splitter.width(), 0])
            return

        total_width = self.splitter.width()
        if total_width > 0:
            central_width = int(total_width * 0.70)
            side_width = total_width - central_width
            if central_width < self.MIN_CENTRAL_WIDTH:
                central_width = self.MIN_CENTRAL_WIDTH
                side_width = total_width - self.MIN_CENTRAL_WIDTH
            self.splitter.setSizes([central_width, side_width])
        else:
            self.splitter.setSizes([700, 300])

    def toggle_side_panel_notification(self, colapsado: bool):
        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")
        if current_mode == "floating":
            return

        if hasattr(self, "splitter") and self.splitter:
            sizes = self.splitter.sizes()
            total = sum(sizes)
            if total > 0:
                if colapsado:
                    self.splitter.setSizes([total - 40, 40])
                else:
                    central_width = int(total * 0.70)
                    side_width = total - central_width
                    if central_width < self.MIN_CENTRAL_WIDTH:
                        central_width = self.MIN_CENTRAL_WIDTH
                        side_width = total - self.MIN_CENTRAL_WIDTH
                    self.splitter.setSizes([central_width, side_width])

            self.splitter.update()
            self.splitter.repaint()

        if hasattr(self, "central_manager") and hasattr(self.central_manager, "get_container"):
            container = self.central_manager.get_container()
            if container:
                container.update()
                container.repaint()

    def rebuild_side_panel(self):
        if not hasattr(self, "side_manager") or not self.side_manager:
            return

        current_panels = {}
        old_container = getattr(self.side_manager, "container", None)

        if old_container:
            if hasattr(old_container, "panels"):
                current_panels = dict(old_container.panels)

            if getattr(old_container, "current_mode", "") == "floating" and hasattr(old_container, "floating_window"):
                if old_container.floating_window:
                    old_container.floating_window.close()

            old_container.setParent(None)
            old_container.deleteLater()

        new_container = SidePanelContainer(title="Side Panel", workspace_manager=self, parent=self)
        self.side_manager.container = new_container

        if hasattr(new_container, "toggle_requested"):
            new_container.toggle_requested.connect(self.toggle_side_panel_notification)

        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")
        if current_mode != "floating":
            new_container.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            self.splitter.addWidget(new_container)
            self.splitter.setStretchFactor(0, 7)
            self.splitter.setStretchFactor(1, 3)
            new_container.setVisible(True)
        else:
            new_container.setVisible(False)
            self.splitter.setStretchFactor(0, 1)

        if current_panels:
            new_container.panels = current_panels
            if hasattr(new_container, "reattach_panels_to_new_container"):
                new_container.reattach_panels_to_new_container(new_container)

        self._configure_splitter()
        self._apply_initial_splitter_sizes()
        self.splitter.update()
        self.splitter.repaint()

    def reattach_panels_to_new_container(self, new_container):
        for panel_id, panel in list(self.panels.items()):
            title = self.panel_titles.get(panel_id, panel_id.replace("_", " ").title())

            if hasattr(panel, "reattach") and callable(panel.reattach):
                panel.reattach(new_container)
            elif new_container and hasattr(new_container, "add_panel"):
                new_container.add_panel(panel_id, panel, title)

            if panel:
                panel.setVisible(True)

    # =====================================================================
    # MODULE AND COMPONENT MANAGEMENT
    # =====================================================================

    def get_modulo_ativo(self):
        if hasattr(self, 'module_manager'):
            return self.module_manager.get_active_module()
        return None

    def on_module_changed(self, module_id: str):
        if hasattr(self, 'module_manager'):
            self.module_manager.on_module_changed(module_id)

    def open_component_selector(self):
        logger.info("Solicitação para abrir o seletor de componentes.")
        self.component_handler.abrir_seletor()

    # =====================================================================
    # Diagnóstico, Logs e Reset
    # =====================================================================

    def log_debug_state(self, level: int = logging.INFO):
        if hasattr(self, "debug_inspector") and self.debug_inspector:
            self.debug_inspector.log_full_state(level=level)

    def reset_workspace(self):
        logger.info("Iniciando o reset completo do workspace.")
        self.registry.clear_all()

        if hasattr(self, "modules") and hasattr(self.module_manager, "tab_controller"):
            if hasattr(self.module_manager.tab_controller, "clear_tabs"):
                self.module_manager.tab_controller.clear_tabs()
            elif hasattr(self.module_manager.tab_controller, "clear_all"):
                self.module_manager.tab_controller.clear_all()
            elif hasattr(self.module_manager.tab_controller, "clear"):
                self.module_manager.tab_controller.clear()

        self.toolbar_manager.clear_all()

        if hasattr(self.side_manager, 'clear_all'):
            self.side_manager.clear_all()

        self.central_manager.clear()
        logger.debug(f"Estado atual pós-reset - Módulos ativos: {self.registry.list_active_modules()}")