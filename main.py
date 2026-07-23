import ctypes
import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

from PySide6 import QtCore, QtWidgets
import vtk

from core.components.bases.base_tool.tool_manager import ToolManager
from core.home_page.flow.flow_editor import PaginaEditorFluxo
from core.home_page.home_page import Home_page
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage
from core.icons.icons_manager import IconManager
from core.localization.translator import tr
from core.scene.events.event_bus import EventBus
from core.scene.io.importer import ObjectImporter
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.scene_manager import SceneManager
from core.scene.scene_state import SceneState
from core.scene.selection.selection_manager import SelectionManager
from core.settings.settings_app_manager import settings
from core.settings.settings_page import PaginaConfig
from core.workspace.models.module_factory import ModuleFactory
from core.workspace.workspace_manager import WorkspaceManager
from modules.base_module.base_module import FluxoBase

# Configuração básica do Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
)

logger = logging.getLogger("OpenCMF.Main")

# Desativa warnings do VTK
vtk.vtkObject.GlobalWarningDisplayOff()


def get_resource_path() -> Path:
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))


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
            self.base_dir = get_resource_path()
            self.current_patient_path = None
            self.workflow = None

            IconManager.set_base_path(self.base_dir / "appearance" / "icons")
            self._setup_scene_components()
            self._setup_core_widgets()
            self._setup_context()
            self._setup_signals()
            self._setup_appearance()
        except Exception as e:
            logger.critical(f"Erro na inicialização: {e}", exc_info=True)
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
        self.project_service = ProjectServiceHomePage(
            self.base_dir / "patients"
        )

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

    def _setup_signals(self):
        """Conecta todos os sinais da aplicação."""
        # Home Page
        self.home.projeto_selecionado.connect(self.on_patient_selected)
        self.home.fluxo_escolhido.connect(self.start_workflow)
        self.home.editor_solicitado.connect(
            lambda: self.stack.setCurrentWidget(self.flow_editor)
        )
        self.home.config_solicitada.connect(
            lambda: self.stack.setCurrentWidget(self.settings_page)
        )

        # Settings Page
        self.settings_page.tema_alterado.connect(self.apply_theme)
        self.settings_page.voltar_solicitado.connect(self.back_to_home)

        # Workspace Header
        self.workspace.header.home_requested.connect(self.back_to_home)
        self.workspace.header.module_changed.connect(self.workspace.on_module_changed)

    def _abrir_ajuda(self):
        """Método auxiliar para abrir a ajuda como janela modal."""
        from core.settings.help.help_page import HelpPage
        help_win = HelpPage(parent=self)
        help_win.exec()

    def _setup_appearance(self):
        """Configura aparência inicial da janela."""
        self.setGeometry(150, 50, 1024, 650)
        self.setWindowTitle(
            tr("main.window_title", settings.get("app_info", "title", "OpenCMF"))
        )

        theme = settings.get("preferencias", "tema", "dark")
        self.apply_theme_by_name(theme)
        self.setup_icon()

    # ======================= Theme & Icons =======================

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
            logger.info(f"Tema alterado para: {theme_name}")
        except Exception as e:
            logger.error(f"Erro ao aplicar tema: {e}")

        self.setup_icon()
        self.theme_changed.emit()

    def apply_theme_by_name(self, theme_name: str):
        """Aplica um tema pelo nome."""
        qss_path = self.base_dir / "appearance" / "themes" / f"{theme_name}.qss"
        if qss_path.exists():
            QtWidgets.QApplication.instance().setStyleSheet(
                qss_path.read_text(encoding="utf-8")
            )

    def setup_icon(self):
        """Define o ícone da aplicação conforme o tema atual."""
        theme = settings.get("preferencias", "tema", "dark")
        color = "#FFFFFF" if theme == "dark" else "#333333"

        manager = IconManager.get_instance()
        app_icon = manager.get_icon("cmf", color=color)

        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
            QtWidgets.QApplication.setWindowIcon(app_icon)

    # ======================= Navigation =======================

    def back_to_home(self):
        """Retorna para a tela inicial."""
        if hasattr(self.home, 'update_list'):
            self.home.update_list()
        self.stack.setCurrentWidget(self.home)

    # ======================= Patient & Workflow =======================

    def on_patient_selected(self, path: str, _mode: str):
        """Callback quando um paciente é selecionado na Home."""
        self.current_patient_path = str(Path(path).resolve())

        if hasattr(self, 'importer'):
            self.importer.patient_path = Path(self.current_patient_path)

        default_flow = self.base_dir / "flows" / "default_flow.json"
        if default_flow.exists():
            self.start_workflow(str(default_flow))
        else:
            logger.warning(f"Fluxo padrão não encontrado em: {default_flow}")

    def start_workflow(self, config_path: str):
        """Inicia um workflow a partir de um arquivo de configuração."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.workspace.reset_workspace()
            self.workflow = FluxoBase(config)
            self.workspace.set_patient_path(self.current_patient_path)

            QtCore.QTimer.singleShot(0, self._load_workflow_modules)

        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Erro ao carregar o workflow '{config_path}': {e}")
            self.workspace.status_bar_manager.showMessage(f"Erro ao carregar fluxo: {e}")

    def _load_workflow_modules(self):
        """Carrega os módulos definidos no workflow."""
        if not self.workflow:
            return

        self.workspace.registry.clear_all()
        self.workspace.header.clear_tabs()

        for module_id in self.workflow.sequencia:
            try:
                module_class = self.project_service.get_module_class(module_id)
                if not module_class:
                    logger.warning(f"Módulo '{module_id}' não encontrado.")
                    continue

                ModuleFactory.register(module_id, module_class)

                module = self.workspace.registry.get_or_create_module(module_id)
                if not module:
                    continue

                title = getattr(module, 'nome', module_id)
                self.workspace.header.add_module_tab(module_id, title)

            except Exception as e:
                logger.error(f"Erro ao carregar o módulo '{module_id}': {e}", exc_info=True)
                self.workspace.status_bar_manager.showMessage(
                    f"Erro ao carregar {module_id}", 3000
                )

        self.stack.setCurrentWidget(self.workspace)

        if self.workspace.header.tab_bar.count() > 0:
            self.workspace.header.tab_bar.setCurrentIndex(0)
            self.sync_active_module()

    def sync_active_module(self):
        """Sincroniza o paciente atual com o módulo ativo no workspace."""
        module = self.workspace.get_modulo_ativo()
        if not module:
            return

        if self.current_patient_path and hasattr(module, 'inicializar'):
            module.inicializar(self.current_patient_path)

    # ======================= Main Entry =======================

    @staticmethod
    def run():
        # Ativa o redirecionamento do print() logo no início da execução
        DebugLogger.setup_redirect()

        if sys.platform == "win32":
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("opencmf.1.0")
            except Exception as e:
                logger.warning(f"Não foi possível definir o AppUserModelID: {e}")

        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("OpenCMF")
        app.setOrganizationName("OpenCMF")

        try:
            window = MainWindow()
            window.show()
            exit_code = app.exec()
            ModuleFactory.clear_cache()
            sys.exit(exit_code)
        except Exception as e:
            logger.critical(f"Erro fatal na inicialização da aplicação: {e}", exc_info=True)
            sys.exit(1)


class DebugLogger:
    """Classe responsável por gerenciar logs, debugs, interceptar o print()
    e enriquecer os registros com dados do contexto, paciente, cena e workspace.
    """

    _instance = None

    def __init__(self, name: str = "OpenCMF.Stdout"):
        self.logger = logging.getLogger(name)
        self.terminal = sys.stdout  # Mantém a referência original caso precise
        self._application_context: Optional[Any] = None

    @classmethod
    def setup_redirect(cls):
        """Substitui o sys.stdout global para capturar todas as chamadas de print()."""
        if cls._instance is None:
            cls._instance = cls()
            sys.stdout = cls._instance
        return cls._instance

    @classmethod
    def get_instance(cls) -> Optional["DebugLogger"]:
        return cls._instance

    def set_context(self, context: Any):
        """Define o contexto global da aplicação para extração de dados em tempo de execução."""
        self._application_context = context

    def write(self, message: str):
        """Intercepta o que seria enviado para o print() e envia para o logger."""
        message = message.strip()
        if message:  # Evita registrar linhas em branco geradas por prints vazios
            self.logger.debug(message)

    def flush(self):
        """Necessário para manter compatibilidade com o buffer do sys.stdout."""
        pass

    def log_system_state(self, message: str, level: str = "info"):
        """Registra uma mensagem enriquecida com metadados do estado atual da aplicação."""
        state_data = self.get_current_state_info()
        enriched_message = f"{message} | System State: {state_data}"

        log_method = getattr(self.logger, level.lower(), self.logger.debug)
        log_method(enriched_message)

    def get_current_state_info(self) -> dict:
        """Extrai informações consolidadas do estado do paciente, cena e workspace."""
        info = {
            "patient_path": None,
            "scene_state": None,
            "active_module": None,
            "registered_objects_count": 0,
            "actors_count": 0
        }

        if not self._application_context:
            return info

        ctx = self._application_context

        # Extrai caminho do paciente do ProjectService ou Workspace
        try:
            if hasattr(ctx, "project_service") and ctx.project_service:
                # Caso haja um caminho ativo gerenciado
                pass
            if hasattr(ctx, "workspace_manager") and ctx.workspace_manager:
                if hasattr(ctx.workspace_manager, "current_patient_path"):
                    info["patient_path"] = ctx.workspace_manager.current_patient_path
        except Exception:
            pass

        # Extrai dados do SceneManager e Registries
        try:
            if hasattr(ctx, "scene_manager") and ctx.scene_manager:
                if hasattr(ctx.scene_manager, "state"):
                    info["scene_state"] = str(ctx.scene_manager.state)

            if hasattr(ctx, "object_registry") and ctx.object_registry:
                if hasattr(ctx.object_registry, "get_all"):
                    info["registered_objects_count"] = len(ctx.object_registry.get_all())

            if hasattr(ctx, "actor_registry") and ctx.actor_registry:
                if hasattr(ctx.actor_registry, "get_all"):
                    info["actors_count"] = len(ctx.actor_registry.get_all())
        except Exception:
            pass

        # Extrai dados do Workspace / Módulo Ativo
        try:
            if hasattr(ctx, "workspace_manager") and ctx.workspace_manager:
                if hasattr(ctx.workspace_manager, "get_modulo_ativo"):
                    active_mod = ctx.workspace_manager.get_modulo_ativo()
                    if active_mod:
                        info["active_module"] = getattr(active_mod, "nome", type(active_mod).__name__)
        except Exception:
            pass

        return info


if __name__ == "__main__":
    MainWindow.run()