import ctypes
import json
import sys
from pathlib import Path
from typing import Any, Optional

from PySide6 import QtCore, QtWidgets
import vtk

vtk.vtkObject.GlobalWarningDisplayOff()

# Home page
from core.home_page.flow.flow_editor import PaginaEditorFluxo
from core.home_page.home_page import Home_page
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage

# Settings
from settings.settings_app_manager import settings
from settings.settings_page import PaginaConfig

from settings.icons.icons_manager import IconManager
from settings.localization.translator import tr

from list_paths import BASE_DIR, PATIENTS_DIR, THEMES_DIR, DEFAULT_FLOW_PATH, ICONS_DIR

from settings.logs.logger_manager import Main_Logger, main_logger

Main_Logger.setup_redirect()

# Scene
from core.scene.events.event_bus import EventBus
from core.scene.io.importer import ObjectImporter
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.scene_manager import SceneManager
from core.scene.scene_state import SceneState
from core.scene.selection.selection_manager import SelectionManager

# Components
from core.components.bases.base_tool.tool_manager import ToolManager

# Workspace
from core.workspace.models.module_factory import ModuleFactory
from core.workspace.workspace_manager import WorkspaceManager
from modules.base_module.base_module import FluxoBase


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
    ):
        self.scene_manager = scene_manager
        self.project_service = project_service
        self.event_bus = event_bus
        self.object_registry = object_registry
        self.tool_manager = tool_manager
        self.workspace_manager = workspace_manager


class MainWindow(QtWidgets.QMainWindow):
    """Janela principal da aplicação OpenCMF."""

    theme_changed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        try:
            self.base_dir = BASE_DIR
            self.current_patient_path = None
            self.workflow = None

            IconManager.get_instance().set_base_path(ICONS_DIR)
            self._setup_scene_components()
            self._setup_core_widgets()
            self._setup_context()
            self._setup_signals()
            self._setup_appearance()
        except Exception as e:
            main_logger.critical(f"Erro na inicialização: {e}", exc_info=True)
            QtWidgets.QMessageBox.critical(
                self,
                "Erro",
                f"Falha ao inicializar aplicação: {e}"
            )
            raise

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
        self.importer = ObjectImporter(patient_path=".")

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
        self.project_service = ProjectServiceHomePage(PATIENTS_DIR)

        self.context = ApplicationContext(
            scene_manager=self.scene_manager,
            project_service=self.project_service,
            event_bus=self.event_bus,
            object_registry=self.object_registry,
            tool_manager=self.tool_manager,
            workspace_manager=self.workspace,
        )

        if hasattr(self.workspace, 'set_context'):
            self.workspace.set_context(self.context)

        ModuleFactory.set_context(self.context)

        # Configura o contexto global na instância do DebugLogger
        debug_instance = Main_Logger.get_instance()
        if debug_instance:
            debug_instance.set_context(self.context)

    def _setup_signals(self):
        """Conecta todos os sinais da aplicação."""
        self.home.projeto_selecionado.connect(self.on_patient_selected)
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

    def _setup_appearance(self):
        """Configura aparência inicial da janela."""
        self.setWindowTitle(
            tr("main.window_title", settings.get("app_info", "title", "OpenCMF"))
        )

        theme = settings.get("preferencias", "tema", "dark")
        self.apply_theme_by_name(theme)
        self.setup_icon()

        # Abre a janela maximizada
        self.showMaximized()

    def apply_theme(self, qss_path_str: str):
        """Aplica tema a partir do caminho do arquivo QSS."""
        qss_path = Path(qss_path_str)
        if not qss_path.exists():
            return

        theme_name = qss_path.stem
        try:
            self.apply_theme_by_name(theme_name)
            settings.set("preferencias", "tema", theme_name)
            settings.save()
            main_logger.info(f"Tema alterado para: {theme_name}")
        except Exception as e:
            main_logger.error(f"Erro ao aplicar tema: {e}")

        self.setup_icon()
        self.theme_changed.emit()

    def apply_theme_by_name(self, theme_name: str):
        qss_path = THEMES_DIR / f"{theme_name}.qss"
        if qss_path.exists():
            QtWidgets.QApplication.instance().setStyleSheet(
                qss_path.read_text(encoding="utf-8")
            )

    def setup_icon(self):
        theme = settings.get("preferencias", "tema", "dark")
        color = "#FFFFFF" if theme == "dark" else "#333333"

        manager = IconManager.get_instance()
        app_icon = manager.get_icon("cmf", color=color)

        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
            QtWidgets.QApplication.setWindowIcon(app_icon)

    def back_to_home(self):
        if hasattr(self.home, 'update_list'):
            self.home.update_list()
        self.stack.setCurrentWidget(self.home)

    def on_patient_selected(self, path: str, _mode: str):
        self.current_patient_path = str(Path(path).resolve())

        if hasattr(self, 'importer'):
            self.importer.patient_path = Path(self.current_patient_path)

        if DEFAULT_FLOW_PATH.exists():
            self.start_workflow(str(DEFAULT_FLOW_PATH))
        else:
            main_logger.warning(f"Fluxo padrão não encontrado em: {DEFAULT_FLOW_PATH}")

    def start_workflow(self, config_path: str):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.workspace.reset_workspace()
            self.workflow = FluxoBase(config)
            self.workspace.set_patient_path(self.current_patient_path)

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
            f"[MainWindow] Carregando fluxo '{self.workflow.nome}' com a sequência de etapas: {self.workflow.sequencia}")
        self.workspace.reset_workspace()

        # 1. Registra as classes dos módulos na fábrica e informa o registry da workspace
        for module_id in self.workflow.sequencia:
            try:
                main_logger.info(f"[MainWindow] Buscando classe para o module_id: '{module_id}' via project_service...")
                module_class = self.project_service.get_module_class(module_id)

                if not module_class:
                    main_logger.error(
                        f"[MainWindow] FALHA: Módulo '{module_id}' retornado como None pelo project_service.get_module_class()!")
                    continue

                main_logger.info(
                    f"[MainWindow] Classe encontrada para '{module_id}': {module_class.__name__}. Registrando na ModuleFactory...")
                ModuleFactory.register(module_id, module_class)

                if hasattr(self.workspace.registry, "register_active_module"):
                    self.workspace.registry.register_active_module(module_id)
                    main_logger.info(f"[MainWindow] Módulo '{module_id}' registrado com sucesso no WorkspaceRegistry.")

            except Exception as e:
                main_logger.error(f"[MainWindow] Erro crítico ao registrar o módulo '{module_id}': {e}", exc_info=True)
                if hasattr(self.workspace, 'status_bar_manager') and self.workspace.status_bar_manager:
                    self.workspace.status_bar_manager.showMessage(
                        f"Erro ao carregar {module_id}", 3000
                    )

        # 2. Exibe a workspace na tela principal
        main_logger.info("[MainWindow] Exibindo o widget da workspace na pilha principal (QStackedWidget)...")
        self.stack.setCurrentWidget(self.workspace)

        # 3. Delega o carregamento visual e a criação das abas inteiramente para o WorkspaceModuleManager
        if hasattr(self.workspace, 'module_manager') and hasattr(self.workspace.module_manager, 'load_modules'):
            main_logger.info(
                "[MainWindow] Disparando o carregamento visual dos módulos através do module_manager.load_modules()...")
            self.workspace.module_manager.load_modules()
        else:
            main_logger.warning(
                "[MainWindow] O WorkspaceModuleManager não foi encontrado ou não possui o método 'load_modules'.")

        # 4. Sincroniza o primeiro módulo ativo se houver abas no TabController
        if hasattr(self.workspace, 'module_manager') and self.workspace.module_manager.tab_controller.tabs:
            main_logger.info("[MainWindow] Abas detectadas no TabController. Ativando o índice 0 e sincronizando...")
            self.workspace.module_manager.tab_controller.set_active(0)
            self.sync_active_module()
        else:
            main_logger.warning("[MainWindow] Nenhuma aba encontrada no TabController após carregar os módulos.")

        QtCore.QTimer.singleShot(150, lambda: self.workspace.log_debug_state() if hasattr(self.workspace,
                                                                                          "log_debug_state") else None)

    def sync_active_module(self):
        module = self.workspace.get_modulo_ativo()
        if not module:
            return

        if self.current_patient_path and hasattr(module, 'inicializar'):
            module.inicializar(self.current_patient_path)

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