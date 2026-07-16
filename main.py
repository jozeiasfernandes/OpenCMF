import sys
import json
import logging
import ctypes
import vtk
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore

from modules.base_module.base_module import FluxoBase
from core.localization.translator import tr
from core.workspace.workspace_manager import WorkspaceManager
from core.home_page.settings_app import settings
from core.home_page.home_page import Home_page
from core.home_page.flow.flow_editor import PaginaEditorFluxo
from core.home_page.settings.settings_page import PaginaConfig
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage
from core.icons.icons_manager import IconManager
from core.workspace.module_factory import ModuleFactory

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
logger = logging.getLogger("OpenCMF.Main")
vtk.vtkObject.GlobalWarningDisplayOff()

def get_resource_path() -> Path:
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))

class MainWindow(QtWidgets.QMainWindow):
    theme_changed = QtCore.Signal()
    def __init__(self):
        super().__init__()
        self.base_dir = get_resource_path()
        IconManager.set_base_path(self.base_dir / "appearance" / "icons")
        self.project_service = ProjectServiceHomePage(self.base_dir / "patients")
        self.current_patient_path: Optional[str] = None
        self.workflow: Optional[FluxoBase] = None

        self._setup_core()
        self._setup_signals()
        self._setup_appearance()

    def _setup_core(self):
        self.stack = QtWidgets.QStackedWidget()
        self.home = Home_page()
        self.flow_editor = PaginaEditorFluxo()

        self.workspace = WorkspaceManager()

        self.settings_page = PaginaConfig()

        self.setCentralWidget(self.stack)

        for widget in [self.home, self.flow_editor, self.workspace, self.settings_page]:
            self.stack.addWidget(widget)

    def _setup_signals(self):
        # Sinais da Home Page
        self.home.projeto_selecionado.connect(self.on_patient_selected)
        self.home.fluxo_escolhido.connect(self.start_workflow)
        self.home.editor_solicitado.connect(
            lambda: self.stack.setCurrentWidget(self.flow_editor)
        )
        self.home.config_solicitada.connect(
            lambda: self.stack.setCurrentWidget(self.settings_page)
        )

        # Sinais da Settings Page
        self.settings_page.tema_alterado.connect(self.apply_theme)
        self.settings_page.voltar_solicitado.connect(self.back_to_home)

        # Sinais do Header (Workspace)
        self.workspace.header.home_requested.connect(self.back_to_home)
        self.workspace.header.module_changed.connect(self.sync_active_module)

    def _setup_appearance(self):
        self.setGeometry(150, 50, 1024, 650)
        self.setWindowTitle(tr("main.window_title", settings.get("app_info", "titulo", "OpenCMF")))

        theme = settings.get("preferencias", "tema", "dark")

        self.apply_theme_by_name(theme)
        self.setup_icon()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("IconManager deve ser inicializado com set_base_path() antes de ser usado.")
        return cls._instance

    def apply_theme(self, qss_path_str: str):
        qss_path = Path(qss_path_str)
        if qss_path.exists():
            theme_name = qss_path.stem  # Defina o nome primeiro
            try:
                self.apply_theme_by_name(theme_name)
                settings.set("preferencias", "tema", theme_name)
                settings.save()
                logger.info(f"Tema alterado para: {theme_name}")
            except Exception as e:
                logger.error(f"Erro ao aplicar tema: {e}")

        # Chama a atualização de ícones e emite o sinal para os outros widgets
        self.setup_icon()
        self.theme_changed.emit()

    def apply_theme_by_name(self, theme_name):
        qss_path = self.base_dir / "appearance" / "themes" / f"{theme_name}.qss"
        if qss_path.exists():
            QtWidgets.QApplication.instance().setStyleSheet(qss_path.read_text(encoding="utf-8"))


    def setup_icon(self):
        theme = settings.get("preferencias", "tema", "dark")
        cor_icone = "#FFFFFF" if theme == "dark" else "#333333"

        manager = IconManager.get_instance()
        app_icon = manager.get_icon("cmf", color=cor_icone)

        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
            QtWidgets.QApplication.setWindowIcon(app_icon)

    def back_to_home(self):
        if hasattr(self.home, 'update_list'):
            self.home.update_list()
        self.stack.setCurrentWidget(self.home)

    def on_patient_selected(self, path: str, _mode: str):
        self.current_patient_path = str(Path(path).resolve())
        default_flow = self.base_dir / "flows" / "default_flow.json"
        if default_flow.exists():
            self.start_workflow(str(default_flow))

    def start_workflow(self, config_path: str):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Limpeza de estado anterior
            self.workspace.registry.clear_all()
            self.workspace.header.clear_tabs()

            if hasattr(self.workspace, 'toolbar_manager'):
                self.workspace.toolbar_manager.clear_all()

            # Inicialização do novo workflow
            self.workflow = FluxoBase(config)

            # Define o contexto do paciente
            if hasattr(self.workspace, 'set_patient_path'):
                self.workspace.set_patient_path(self.current_patient_path)

            # Carrega os módulos após o evento atual
            QtCore.QTimer.singleShot(0, self._load_workflow_modules)

        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Erro ao carregar o workflow '{config_path}': {e}")
            self.workspace.status_bar_manager.showMessage(f"Erro ao carregar fluxo: {e}")

    def _load_workflow_modules(self):
        if not self.workflow:
            return

        # Limpeza de módulos anteriores
        self.workspace.registry.clear_all()
        self.workspace.header.clear_tabs()

        for module_id in self.workflow.sequencia:
            try:
                module_class = self.project_service.get_module_class(module_id)
                if not module_class:
                    logger.warning(f"Módulo '{module_id}' não encontrado.")
                    continue

                # Registro e criação do módulo
                ModuleFactory.register(module_id, module_class)
                module = self.workspace.registry.get_or_create_module(module_id)

                # Adiciona aba no header
                title = getattr(module, 'module_title', module_id)
                self.workspace.header.add_module_tab(module_id, title)

            except Exception as e:
                logger.error(f"Erro ao carregar o módulo '{module_id}': {e}")
                self.workspace.status_bar_manager.showMessage(f"Erro ao carregar {module_id}", 3000)

        # Ativa o workspace
        self.stack.setCurrentWidget(self.workspace)

        # Seleciona o primeiro módulo por padrão
        if self.workspace.header.tab_bar.count() > 0:
            self.workspace.header.tab_bar.setCurrentIndex(0)

    def sync_active_module(self):
        module = self.workspace.get_modulo_ativo()
        if module and self.current_patient_path and hasattr(module, 'inicializar'):
            module.inicializar(self.current_patient_path)

    def on_step_complete(self, module: QtWidgets.QWidget):
        path = getattr(module, 'pasta_paciente', None)
        if path:
            self.current_patient_path = str(Path(path).resolve())

if __name__ == "__main__":
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("opencmf.1.0")

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())