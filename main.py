import ctypes
import json
import sys
from pathlib import Path
from typing import Any, Optional

from PySide6 import QtCore, QtWidgets
import vtk
vtk.vtkObject.GlobalWarningDisplayOff()

# Patient
from core.application.patient.patient_manager import PatientManager
from core.application.patient.patient_config_manager import PatientConfigManager
from core.settings.paths.list_paths import PATIENTS_DIR

# Home page & Project Manager
from core.application.home_page.home_page import Home_page
from core.application.home_page.project_manager.project_service import ProjectServiceHomePage
from application.flows.flows_editor.flows_editor import PaginaEditorFluxo

# Scene
from core.application.scene.scene_manager import SceneManager
from core.application.scene.events.event_bus import EventBus
from core.application.scene.io.importer import ObjectImporter
from core.application.scene.registry.actor_registry import ActorRegistry
from core.application.scene.registry.object_registry import ObjectRegistry
from core.application.scene.scene_state import SceneState
from core.application.scene.selection.selection_manager import SelectionManager

# Components
from core.components.bases.base_tool.tool_manager import ToolManager

# Import Window
from core.application.imports.import_window.import_window import ImportWindow

# Workspace & Modules
from core.workspace.models.module_factory import ModuleFactory
from core.workspace.workspace_manager import WorkspaceManager
from core.workspace.modules.module_service import ModuleService
from core.workspace.modules.base.flow_base_module import FlowModuleBase


# Settings
from core.settings.localization.translator import tr

from core.settings.settings_app_manager import settings
from core.settings.settings_page import PaginaConfig

    ## Icons
from core.settings.icons.icon_manager import IconManager
from core.settings.paths.list_paths import BASE_DIR, ICONS_DIR

    ## Themes
from core.settings.themes.theme_manager import ThemeManager
from core.settings.logs.logger_manager import themes_logger

    ## Logs
from core.settings.logs.logger_manager import Main_Logger, main_logger
Main_Logger.setup_redirect()


class ApplicationContext:
    """Contexto injetado nas fábricas e módulos."""

    def __init__(
            self,
            scene_manager: Optional[SceneManager] = None,
            project_service: Optional[ProjectServiceHomePage] = None,
            event_bus: Optional[EventBus] = None,
            object_registry: Optional[ObjectRegistry] = None,
            tool_manager: Any = None,
            workspace_manager: Optional[WorkspaceManager] = None,
            patient_manager: Optional[PatientManager] = None,
            main_window: Optional[Any] = None,
    ):
        self.scene_manager = scene_manager
        self.project_service = project_service
        self.event_bus = event_bus
        self.object_registry = object_registry
        self.tool_manager = tool_manager
        self.workspace_manager = workspace_manager
        self.patient_manager = patient_manager
        self.main_window = main_window

    def open_import_window(self):
        """Método de utilidade no contexto para disparar a janela de importação."""
        if self.main_window and hasattr(self.main_window, 'open_import_window'):
            self.main_window.open_import_window()


class MainWindow(QtWidgets.QMainWindow):
    """Janela principal da aplicação OpenCMF."""

    theme_changed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        try:
            self.base_dir = BASE_DIR
            self.workflow = None
            self.import_window_instance: Optional[ImportWindow] = None

            IconManager.get_instance().set_base_path(ICONS_DIR)
            self.theme_manager = ThemeManager(QtWidgets.QApplication.instance())

            # Inicializa serviços principais antes dos componentes de cena/contexto
            self.project_service = ProjectServiceHomePage(PATIENTS_DIR)
            self.config_manager = PatientConfigManager()
            self.patient_manager = PatientManager(config_manager=self.config_manager)

            self._setup_scene_components()
            self._setup_core_widgets()
            self._setup_context()
            self._setup_signals()
            self._setup_appearance()
        except Exception as e:
            main_logger.critical(f"Erro na inicialização: {e}", exc_info=True)
            QtWidgets.QMessageBox.critical(
                self,
                tr("common.error", "Erro"),
                f"Falha ao inicializar aplicação: {e}"
            )
            raise

    # =========================================================================
    # CONFIGURATION AND INITIALIZATION (_setup_*)
    # =========================================================================

    def _setup_scene_components(self):
        """Inicializa os componentes da cena 3D."""
        self.event_bus = EventBus()
        self.scene_state = SceneState()

        self.object_registry = ObjectRegistry()
        self.actor_registry = ActorRegistry()
        self.selection_manager = SelectionManager(
            state=self.scene_state,
            event_bus=self.event_bus
        )

        initial_path = self.patient_manager.current_path or "."
        self.importer = ObjectImporter(patient_path=Path(initial_path))

        self.scene_manager = SceneManager(
            state=self.scene_state,
            event_bus=self.event_bus,
            object_registry=self.object_registry,
            actor_registry=self.actor_registry,
            selection_manager=self.selection_manager,
            importer=self.importer,
        )

        self.tool_manager = ToolManager()

    def _setup_core_widgets(self):
        """Configura os widgets principais e o QStackedWidget."""
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = Home_page()
        self.flow_editor = PaginaEditorFluxo()
        self.workspace = WorkspaceManager()
        self.settings_page = PaginaConfig(workspace_manager=self.workspace)

        for widget in [self.home, self.flow_editor, self.workspace, self.settings_page]:
            self.stack.addWidget(widget)

    def _setup_context(self):
        """Configura o contexto da aplicação e o ModuleFactory."""
        self.context = ApplicationContext(
            scene_manager=self.scene_manager,
            project_service=self.project_service,
            event_bus=self.event_bus,
            object_registry=self.object_registry,
            tool_manager=self.tool_manager,
            workspace_manager=self.workspace,
            patient_manager=self.patient_manager,
            main_window=self,
        )

        if hasattr(self.workspace, 'set_context'):
            self.workspace.set_context(self.context)

        ModuleFactory.set_context(self.context)

        debug_instance = Main_Logger.get_instance()
        if debug_instance:
            debug_instance.set_context(self.context)

    def _setup_signals(self):
        """Conecta todos os sinais da aplicação."""
        self.home.fluxo_escolhido.connect(self.start_workflow)
        self.home.editor_solicitado.connect(
            lambda: self.stack.setCurrentWidget(self.flow_editor)
        )
        self.home.config_solicitada.connect(
            lambda: self.stack.setCurrentWidget(self.settings_page)
        )

        self.settings_page.tema_alterado.connect(self.apply_theme)
        self.settings_page.voltar_solicitado.connect(self.back_to_home)

        self.workspace.header.home_requested.connect(self.back_to_home)
        self.workspace.header.module_changed.connect(self.workspace.on_module_changed)

        self.patient_manager.patient_changed.connect(self._on_patient_path_changed)

    def _setup_appearance(self):
        """Configura a aparência inicial (título, tema, ícone e tamanho)."""
        self.setWindowTitle(
            tr("main.window_title", settings.get("app_info", "title", "OpenCMF"))
        )

        theme = settings.tema
        self.apply_theme(theme)
        self.setup_icon()
        self.showMaximized()

    # =========================================================================
    # THEME AND ICON MANAGEMENT
    # =========================================================================

    def apply_theme(self, theme_input: str):
        path = Path(theme_input)
        theme_name = path.stem if path.is_file() else theme_input

        try:
            success = self.theme_manager.apply_static_theme(theme_name)
            if not success:
                success = self.theme_manager.apply_custom_theme()

            if success:
                settings.tema = theme_name
                IconManager.get_instance().clear_cache()
                main_logger.info(f"Tema alterado para: {theme_name}")
            else:
                main_logger.warning(f"Falha ao aplicar o tema: {theme_name}")

        except Exception as e:
            main_logger.error(f"Erro ao aplicar tema '{theme_name}': {e}", exc_info=True)

        self.setup_icon()
        self.theme_changed.emit()

    def apply_theme_by_name(self, theme_name: str):
        """Aplica o tema utilizando o ThemeManager centralizado."""
        themes_logger.info(f"Aplicando tema: {theme_name}", theme_name=theme_name)
        try:
            success = self.theme_manager.apply_static_theme(theme_name)
            if not success:
                success = self.theme_manager.apply_custom_theme()

            if success:
                settings.tema = theme_name
                IconManager.get_instance().clear_cache()
                themes_logger.info(f"Tema alterado com sucesso para: {theme_name}", theme_name=theme_name)
            else:
                themes_logger.warning(f"Falha ao aplicar o tema: {theme_name}", theme_name=theme_name)
        except Exception as e:
            themes_logger.error(f"Erro ao aplicar tema '{theme_name}': {e}", theme_name=theme_name, exc_info=True)

        self.setup_icon()
        self.theme_changed.emit()

    def setup_icon(self):
        manager = IconManager.get_instance()
        app_icon = manager.get_app_icon()

        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
            QtWidgets.QApplication.setWindowIcon(app_icon)

    # =========================================================================
    # WORKFLOWS AND PROCESS FLOWS
    # =========================================================================

    def start_workflow(self, config_path: str):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.workspace.reset_workspace()
            self.workflow = FlowModuleBase(context=config)

            self.workflow.name = config.get("name") or config.get("nome", "Unnamed Flow")

            raw_sequence = config.get("sequence") or config.get("sequencia", [])

            if isinstance(raw_sequence, dict):
                self.workflow.sequencia = list(raw_sequence.keys())
            elif isinstance(raw_sequence, list):
                self.workflow.sequencia = raw_sequence
            else:
                self.workflow.sequencia = []

            if self.patient_manager.current_path:
                self.workspace.set_patient_path(self.patient_manager.current_path)

            QtCore.QTimer.singleShot(0, self._load_workflow_modules)

        except (json.JSONDecodeError, OSError) as e:
            main_logger.error(f"Erro ao carregar o workflow '{config_path}': {e}")
            self.workspace.status_bar_manager.showMessage(f"Erro ao carregar fluxo: {e}")

    def _load_workflow_modules(self):
        if not self.workflow:
            main_logger.warning(
                "[MainWindow] Tentativa de carregar módulos, mas nenhum fluxo (workflow) está definido.")
            return

        main_logger.info(
            f"[MainWindow] Carregando fluxo '{self.workflow.name}' com a sequência de etapas: {self.workflow.sequencia}")

        if hasattr(self.workspace, 'module_manager') and hasattr(self.workspace.module_manager, 'tab_controller'):
            if hasattr(self.workspace.module_manager.tab_controller, 'clear_tabs'):
                self.workspace.module_manager.tab_controller.clear_tabs()

        self.workspace.reset_workspace()

        module_service = ModuleService()

        for module_id in self.workflow.sequencia:
            try:
                main_logger.info(f"[MainWindow] Buscando classe para o module_id: '{module_id}' via module_service...")
                module_class = module_service.get_module_class(module_id)

                if not module_class:
                    error_msg = f"Módulo '{module_id}' não encontrado."
                    main_logger.error(f"[MainWindow] FALHA: {error_msg}")
                    if hasattr(self.workspace, 'status_bar_manager') and self.workspace.status_bar_manager:
                        self.workspace.status_bar_manager.showMessage(error_msg, 4000)
                    continue

                ModuleFactory.register(module_id, module_class)

                if hasattr(self.workspace.registry, "register_active_module"):
                    self.workspace.registry.register_active_module(module_id)

            except Exception as e:
                main_logger.error(f"[MainWindow] Erro crítico ao registrar o módulo '{module_id}': {e}", exc_info=True)
                if hasattr(self.workspace, 'status_bar_manager') and self.workspace.status_bar_manager:
                    self.workspace.status_bar_manager.showMessage(
                        f"Erro ao carregar {module_id}", 3000
                    )

        main_logger.info("[MainWindow] Exibindo o widget da workspace na pilha principal (QStackedWidget)...")
        self.stack.setCurrentWidget(self.workspace)

        # Correção aqui: referenciando corretamente 'module_manager'
        if hasattr(self.workspace, 'module_manager') and hasattr(self.workspace.module_manager, 'load_modules'):
            self.workspace.module_manager.load_modules()

        if self.patient_manager.current_path:
            self.workspace.set_patient_path(self.patient_manager.current_path)

        # Correção aqui também para ativar a primeira aba do fluxo
        if hasattr(self.workspace, 'module_manager') and self.workspace.module_manager.tab_controller.tabs:
            self.workspace.module_manager.tab_controller.set_active(0)
            self.sync_active_module()

        QtCore.QTimer.singleShot(150, lambda: self.workspace.log_debug_state() if hasattr(self.workspace,
                                                                                          "log_debug_state") else None)

    def sync_active_module(self):
        module = self.workspace.get_modulo_ativo()
        if not module:
            return

        current_path = self.patient_manager.current_path
        if current_path and hasattr(module, 'inicializar'):
            module.initialize(current_path)

    # =========================================================================
    # NAVIGATION AND USER EVENTS
    # =========================================================================

    def back_to_home(self):
        if hasattr(self.home, 'update_list'):
            self.home.update_list()
        self.patient_manager.clear()
        self.stack.setCurrentWidget(self.home)

    def open_import_window(self):
        """Abre a janela avançada de importação com suporte ao SceneManager."""
        if not self.patient_manager.current_path:
            QtWidgets.QMessageBox.warning(
                self,
                tr("common.warning", "Aviso"),
                "Por favor, selecione ou crie um paciente antes de abrir o gerenciador de importações."
            )
            return

        if self.import_window_instance is None:
            self.import_window_instance = ImportWindow(scene_manager=self.scene_manager)

        self.import_window_instance.show()
        self.import_window_instance.raise_()
        self.import_window_instance.activateWindow()

    def _on_patient_path_changed(self, new_path: str):
        if new_path and hasattr(self, 'importer'):
            self.importer.patient_path = Path(new_path)

    # =========================================================================
    # APPLICATION EXECUTION
    # =========================================================================

    @staticmethod
    def run():
        if sys.platform == "win32":
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("opencmf.1.0")
            except Exception as e:
                main_logger.warning(f"Não foi possível definir o AppUserModelID: {e}")

        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("OpenCMF")
        app.setOrganizationName("OpenCMF")

        try:
            main_logger.info("Iniciando a aplicação OpenCMF...")
            window = MainWindow()
            window.show()
            exit_code = app.exec()
            ModuleFactory.clear_cache()
            main_logger.info(f"Aplicação encerrada com código: {exit_code}")
            sys.exit(exit_code)
        except Exception as e:
            main_logger.critical(f"Erro fatal na inicialização da aplicação: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    MainWindow.run()