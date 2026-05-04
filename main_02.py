import sys
import json
import logging
import ctypes
import vtk
import traceback
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore, QtGui

from core.base_module.base import FluxoBase
from core.localization.translator import tr
from core.workspace.workspace_manager_02 import WorkspaceManager
from core.home_page.settings_app import settings
from core.home_page.home_page_02 import Home_page
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

        self.stack = QtWidgets.QStackedWidget()
        self.home = Home_page()
        self.flow_editor = PaginaEditorFluxo()
        self.workspace = WorkspaceManager()
        self.settings_page = PaginaConfig()

        self._init_ui()
        self._connect_signals()
        self._load_settings()

    def _init_ui(self):
        self.setGeometry(150, 50, 1024, 650)
        self.setCentralWidget(self.stack)
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.flow_editor)
        self.stack.addWidget(self.workspace)
        self.stack.addWidget(self.settings_page)
        self.setWindowTitle(tr("main.window_title", settings.get("app_info", "titulo", "OpenCMF")))

    def _connect_signals(self):
        self.home.projeto_selecionado.connect(self.on_patient_selected)
        self.home.fluxo_escolhido.connect(self.start_workflow)
        self.home.editor_solicitado.connect(lambda: self.stack.setCurrentWidget(self.flow_editor))
        self.home.config_solicitada.connect(lambda: self.stack.setCurrentWidget(self.settings_page))
        self.workspace.home_solicitada.connect(self.back_to_home)
        self.workspace.config_solicitada.connect(lambda: self.stack.setCurrentWidget(self.settings_page))
        self.settings_page.voltar_solicitado.connect(self.back_to_home)
        self.workspace.currentChanged.connect(self.sync_module)

    def _load_settings(self):
        theme = settings.get("preferencias", "tema", "dark")
        qss_path = self.base_dir / "appearance" / "themes" / f"{theme}.qss"
        if qss_path.exists():
            QtWidgets.QApplication.instance().setStyleSheet(qss_path.read_text(encoding="utf-8"))

    def back_to_home(self):
        if hasattr(self.home, 'update_list'): self.home.update_list()
        self.stack.setCurrentWidget(self.home)

    def on_patient_selected(self, path: str, _mode: str):
        self.current_patient_path = str(Path(path).resolve())
        default_flow = self.base_dir / "flows" / "default_flow.json"
        if default_flow.exists(): self.start_workflow(str(default_flow))

    def start_workflow(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f: config = json.load(f)
            self.workspace.clear()
            self.workflow = FluxoBase(config)
            QtCore.QTimer.singleShot(0, self._load_modules_sequentially)
        except Exception:
            logger.error(traceback.format_exc())

    def _load_modules_sequentially(self):
        if not self.workflow: return
        with QtCore.QSignalBlocker(self.workspace):
            for m_id in self.workflow.sequencia:
                classe = self.project_service.get_module_class(m_id)
                if classe: self.workspace.adicionar_modulo(m_id, classe, on_concluido=self.on_step_done)
        if self.workspace.count() > 0:
            self.stack.setCurrentWidget(self.workspace)
            QtCore.QTimer.singleShot(0, self.sync_module)

    def sync_module(self):
        active = self.workspace.get_modulo_ativo()
        if active and self.current_patient_path and hasattr(active, 'inicializar'):
            active.inicializar(self.current_patient_path)

    def on_step_done(self):
        sender = self.sender()
        if sender and getattr(sender, 'pasta_paciente', None):
            self.current_patient_path = str(Path(sender.pasta_paciente).resolve())

if __name__ == "__main__":
    if sys.platform == "win32": ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("opencmf.1.0")
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())