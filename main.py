import sys
import json
import logging
import ctypes
import vtk
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
from PySide6 import QtWidgets, QtCore, QtGui

from core.base_module.base import FluxoBase
from core.localization.translator import tr
from core.workspace.workspace import WorkspaceManager
from core.home_page.settings_app import settings
from core.home_page.home_page import Home_page
from core.home_page.flow.flow_editor import PaginaEditorFluxo
from core.home_page.extras.settings_page import PaginaConfig
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("OpenCMF.Main")

vtk.vtkObject.GlobalWarningDisplayOff()


def get_resource_path() -> Path:
    base_path = getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)
    return Path(base_path)


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
        self._setup_icon()
        self.setCentralWidget(self.stack)

        for widget in [self.home, self.flow_editor, self.workspace, self.settings_page]:
            self.stack.addWidget(widget)

        title = settings.get("app_info", "titulo", "OpenCMF")
        self.setWindowTitle(tr("main.window_title", title))

    def _setup_icon(self):
        icon_path = self.base_dir / "appearance" / "icons" / "cmf.svg"
        if not icon_path.exists():
            icon_path = icon_path.with_suffix(".ico")

        if icon_path.exists():
            app_icon = QtGui.QIcon(str(icon_path))
            self.setWindowIcon(app_icon)
            QtWidgets.QApplication.setWindowIcon(app_icon)

    def _connect_signals(self):
        self.home.projeto_selecionado.connect(self.on_patient_selected)
        self.home.fluxo_escolhido.connect(self.start_workflow)
        self.home.editor_solicitado.connect(lambda: self.stack.setCurrentWidget(self.flow_editor))
        self.home.config_solicitada.connect(lambda: self.stack.setCurrentWidget(self.settings_page))
        self.flow_editor.voltar_solicitado.connect(self.back_to_home)
        self.workspace.home_solicitada.connect(self.back_to_home)
        self.settings_page.voltar_solicitado.connect(self.back_to_home)
        self.settings_page.tema_alterado.connect(self.update_theme)
        self.workspace.currentChanged.connect(self.sync_module)

    def _load_settings(self):
        theme_name = settings.get("preferencias", "tema", "dark")
        qss_path = self.base_dir / "appearance" / "themes" / f"{theme_name}.qss"
        self.update_theme(str(qss_path))

    def update_theme(self, qss_path: str):
        file = Path(qss_path)
        if not file.exists():
            file = self.base_dir / "appearance" / "themes" / file.name
            if not file.exists():
                return

        app = QtWidgets.QApplication.instance()
        if isinstance(app, QtWidgets.QApplication):
            app.setStyleSheet(file.read_text(encoding="utf-8"))

        settings.set("preferencias", "tema", file.stem)
        settings.save()

    def back_to_home(self):
        self.home.update_list()
        self.stack.setCurrentWidget(self.home)

    def on_patient_selected(self, path: str, _mode: str):
        self.current_patient_path = str(Path(path).resolve())
        default_flow = self.base_dir / "flows" / "default_flow.json"
        if default_flow.exists():
            self.start_workflow(str(default_flow))

    def start_workflow(self, path: str):
        try:
            logger.info(f"Iniciando workflow: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.workspace.blockSignals(True)
            self.workspace.clear()
            self.workflow = FluxoBase(config)

            QtCore.QTimer.singleShot(0, self._load_modules_sequentially)

        except Exception as e:
            logger.error(f"Erro ao carregar workflow: {e}\n{traceback.format_exc()}")
            self.report_error(tr("common.flow_error"), e)

    def _load_modules_sequentially(self):
        if not self.workflow:
            return

        for module_id in self.workflow.sequencia:
            logger.debug(f"Carregando módulo: {module_id}")
            module = self.project_service.carregar_modulo(module_id)

            if module:
                if hasattr(module, 'concluido'):
                    module.concluido.connect(self.on_step_done)
                self.workspace.adicionar_modulo(module_id, module)

        self.workspace.blockSignals(False)
        if self.workspace.count() > 0:
            self.stack.setCurrentWidget(self.workspace)
            QtCore.QTimer.singleShot(100, self.sync_module)

    def sync_module(self):
        active = self.workspace.get_modulo_ativo()
        if active and self.current_patient_path and hasattr(active, 'inicializar'):
            try:
                active.inicializar(self.current_patient_path)
            except Exception as e:
                logger.error(f"Erro na inicialização do módulo: {e}\n{traceback.format_exc()}")

    def on_step_done(self):
        sender = self.sender()
        if sender and hasattr(sender, 'pasta_paciente') and sender.pasta_paciente:
            self.current_patient_path = str(Path(sender.pasta_paciente).resolve())

    def report_error(self, title: str, error: Exception):
        QtWidgets.QMessageBox.critical(self, tr("common.critical_error"), f"{title}\n{error}")


if __name__ == "__main__":
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("opencmf.surgical_planning.1.0")

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Previne crash do VTK com drivers Intel/Nvidia em ambientes Qt
    app.setAttribute(QtCore.Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())