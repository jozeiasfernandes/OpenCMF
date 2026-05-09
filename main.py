import sys
import json
import logging
import ctypes
import vtk
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore

from core.base_module.base import FluxoBase
from core.localization.translator import tr
from core.workspace.workspace_manager import WorkspaceManager
from core.home_page.settings_app import settings
from core.home_page.home_page import Home_page
from core.home_page.flow.flow_editor import PaginaEditorFluxo
from core.home_page.extras.settings_page import PaginaConfig
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
logger = logging.getLogger("OpenCMF.Main")
vtk.vtkObject.GlobalWarningDisplayOff()


def get_resource_path() -> Path:
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_dir = get_resource_path()
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
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.flow_editor)
        self.stack.addWidget(self.workspace)
        self.stack.addWidget(self.settings_page)

    def _setup_signals(self):
        self.home.projeto_selecionado.connect(self.on_patient_selected)
        self.home.fluxo_escolhido.connect(self.start_workflow)
        self.home.editor_solicitado.connect(lambda: self.stack.setCurrentWidget(self.flow_editor))
        self.home.config_solicitada.connect(lambda: self.stack.setCurrentWidget(self.settings_page))

        self.workspace.home_solicitada.connect(self.back_to_home)
        self.workspace.currentChanged.connect(self.sync_active_module)

        self.settings_page.voltar_solicitado.connect(self.back_to_home)

    def _setup_appearance(self):
        self.setGeometry(150, 50, 1024, 650)
        self.setWindowTitle(tr("main.window_title", settings.get("app_info", "titulo", "OpenCMF")))

        theme = settings.get("preferencias", "tema", "dark")
        qss_path = self.base_dir / "appearance" / "themes" / f"{theme}.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

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

            self.workspace.clear()
            self.workflow = FluxoBase(config)
            self.workspace.set_patient_path(self.current_patient_path)  # Define o caminho do paciente
            QtCore.QTimer.singleShot(0, self._load_workflow_modules)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Erro no workflow: {e}")

    def _load_workflow_modules(self):
        if not self.workflow:
            return

        with QtCore.QSignalBlocker(self.workspace):
            for module_id in self.workflow.sequencia:
                module_class = self.project_service.get_module_class(module_id)
                if module_class:
                    self.workspace.adicionar_modulo(
                        module_id,
                        module_class,
                        on_concluido=self.on_step_complete
                    )

        if self.workspace.count() > 0:
            self.stack.setCurrentWidget(self.workspace)
            QtCore.QTimer.singleShot(0, self.sync_active_module)

    def sync_active_module(self):
        module = self.workspace.get_modulo_ativo()
        if module and self.current_patient_path and hasattr(module, 'inicializar'):
            module.inicializar(self.current_patient_path)

    def on_step_complete(self):
        sender = self.sender()
        path = getattr(sender, 'pasta_paciente', None)
        if path:
            self.current_patient_path = str(Path(path).resolve())


if __name__ == "__main__":
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("opencmf.1.0")

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())