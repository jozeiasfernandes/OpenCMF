import sys
import json
import logging
import ctypes
import vtk
from pathlib import Path
from typing import Dict, Any, List, Optional
from PySide6 import QtWidgets, QtCore, QtGui

from core.base_module.base import FluxoBase
from core.localization.translator import tr
from core.workspace.workspace import WorkspaceManager
from core.home_page.settings_app import settings
from core.home_page.home_page import Home_page
from core.home_page.flow.flow_editor import PaginaEditorFluxo
from core.home_page.extras.settings_page import PaginaConfig
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage

vtk.vtkObject.GlobalWarningDisplayOff()
vtk_log = vtk.vtkFileOutputWindow()
vtk_log.SetFileName("vtk_debug.log")
vtk.vtkOutputWindow.GetInstance().SetInstance(vtk_log)


def get_resource_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[0]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_dir = get_resource_path()
        self.project_service = ProjectServiceHomePage(self.base_dir / "patients")

        self.current_patient_path: Optional[str] = None
        self.workflow: Optional[FluxoBase] = None

        self.init_ui()
        self.retranslate_ui()
        self.connect_signals()
        self.load_settings()

    def init_ui(self):
        self.setGeometry(150, 50, 1024, 650)
        self.setup_icon()

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = Home_page()
        self.flow_editor = PaginaEditorFluxo()
        self.workspace = WorkspaceManager()
        self.settings_page = PaginaConfig()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.flow_editor)
        self.stack.addWidget(self.workspace)
        self.stack.addWidget(self.settings_page)

    def retranslate_ui(self):
        title = settings.get("app_info", "titulo", "OpenCMF")
        self.setWindowTitle(tr("main.window_title", title))

    def setup_icon(self):
        icon_path = self.base_dir / "appearance" / "icons" / "cmf.svg"
        if not icon_path.exists():
            icon_path = icon_path.with_suffix(".ico")

        if icon_path.exists():
            app_icon = QtGui.QIcon(str(icon_path))
            self.setWindowIcon(app_icon)
            QtWidgets.QApplication.setWindowIcon(app_icon)

    def connect_signals(self):
        self.home.projeto_selecionado.connect(self.on_patient_selected)
        self.home.fluxo_escolhido.connect(self.start_workflow)
        self.home.editor_solicitado.connect(lambda: self.stack.setCurrentWidget(self.flow_editor))
        self.home.config_solicitada.connect(lambda: self.stack.setCurrentWidget(self.settings_page))

        self.flow_editor.voltar_solicitado.connect(self.back_to_home)
        self.workspace.home_solicitada.connect(self.back_to_home)
        self.settings_page.voltar_solicitado.connect(self.back_to_home)

        self.settings_page.tema_alterado.connect(self.update_theme)
        self.workspace.currentChanged.connect(self.sync_module)

    def load_settings(self):
        theme_name = settings.get("preferencias", "tema", "dark")
        qss_path = self.base_dir / "appearance" / "themes" / f"{theme_name}.qss"
        self.update_theme(str(qss_path))

    def update_theme(self, qss_path: str):
        file = Path(qss_path)
        if not file.exists():
            file = self.base_dir / "appearance" / "themes" / Path(qss_path).name
            if not file.exists(): return

        try:
            style = file.read_text(encoding="utf-8")
            QtWidgets.QApplication.instance().setStyleSheet(style)
            settings.set("preferencias", "tema", file.stem)
            settings.save()
        except Exception as e:
            self.report_error(tr("common.theme_error"), e)

    def back_to_home(self):
        self.home.update_list()
        self.stack.setCurrentWidget(self.home)

    def on_patient_selected(self, path: str, mode: str):
        self.current_patient_path = str(Path(path).resolve())
        self.start_workflow(str(self.base_dir / "flows" / "default_flow.json"))

    def start_workflow(self, path: str):
        file = Path(path)
        if not file.exists(): return

        try:
            config = json.loads(file.read_text(encoding="utf-8"))
            self.build_workspace(config)
            self.stack.setCurrentWidget(self.workspace)
            self.sync_module()
        except Exception as e:
            self.report_error(tr("common.flow_error"), e)

    def build_workspace(self, data: Dict[str, Any]):
        self.workspace.blockSignals(True)
        self.workspace.clear()
        self.workflow = FluxoBase(data)

        for module_id in self.workflow.sequencia:
            if module := self.project_service.carregar_modulo(module_id):
                if hasattr(module, 'inicializar') and self.current_patient_path:
                    module.inicializar(self.current_patient_path)

                module.concluido.connect(self.on_step_done)
                self.workspace.adicionar_modulo(module_id, module)

        self.workspace.blockSignals(False)

    def sync_module(self):
        active = self.workspace.get_modulo_ativo()
        if active and self.current_patient_path and hasattr(active, 'inicializar'):
            active.inicializar(self.current_patient_path)

    def on_step_done(self):
        if sender := self.sender():
            if hasattr(sender, 'pasta_paciente') and sender.pasta_paciente:
                self.current_patient_path = str(Path(sender.pasta_paciente).resolve())

    def report_error(self, title: str, error: Exception):
        logging.error(f"{title}: {error}", exc_info=True)
        QtWidgets.QMessageBox.critical(self, tr("common.critical_error"), f"<b>{title}</b><br>{error}")


if __name__ == "__main__":
    app_id = settings.get("app_info", "id", "opencmf.surgicalplanning.1.0")
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())