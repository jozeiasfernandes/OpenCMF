import sys
import json
import logging
import ctypes
import vtk
from pathlib import Path
from typing import Dict, Any, List, Optional
from PySide6 import QtWidgets, QtCore, QtGui

from core.base_module.base import FluxoBase
from core.base_module.factory import ModuloFactory
from core.localization.translator import tr
from core.workspace import WorkspaceManager

from appearance.settings import settings
from appearance.home_page import Home_page
from appearance.flow.flow_editor import PaginaEditorFluxo
from appearance.extras.settings_page import PaginaConfig

vtk.vtkObject.GlobalWarningDisplayOff()
vtk_log = vtk.vtkFileOutputWindow()
vtk_log.SetFileName("vtk_debug.log")
vtk.vtkOutputWindow.GetInstance().SetInstance(vtk_log)


def get_resource_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.resolve()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_patient_path: Optional[str] = None
        self.instantiated_modules: List[Any] = []
        self.workflow: Optional[FluxoBase] = None
        self.base_dir = get_resource_path()

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
        # CORREÇÃO: Caminho agora aponta para appearance/icons
        icon_path = self.base_dir / "appearance" / "icons" / "cmf.png"

        # Fallback para .ico se o .png não for encontrado
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
        # CORREÇÃO: Caminho agora aponta para appearance/themes
        qss_path = self.base_dir / "appearance" / "themes" / f"{theme_name}.qss"
        self.update_theme(str(qss_path))

    def update_theme(self, qss_path: str):
        file = Path(qss_path)
        if not file.exists():
            # Tenta buscar dentro de appearance/themes caso receba apenas o nome do arquivo
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

    def start_workflow(self, path: str):
        file = Path(path)
        is_registration = any(w in file.name.lower() for w in ["registration", "cadastro"])

        if not is_registration and not self.current_patient_path:
            QtWidgets.QMessageBox.warning(self, tr("common.warning"), tr("home.select_patient_msg"))
            return

        try:
            config = json.loads(file.read_text(encoding="utf-8"))
            self.build_workspace(config)
            self.stack.setCurrentWidget(self.workspace)
            QtCore.QTimer.singleShot(100, self.sync_module)
        except Exception as e:
            self.report_error(tr("common.flow_error"), e)

    def build_workspace(self, data: Dict[str, Any]):
        self.workspace.blockSignals(True)
        self.workspace.clear()
        self.instantiated_modules.clear()
        self.workflow = FluxoBase(data)

        for module_id in self.workflow.sequencia:
            if module := ModuloFactory.carregar_modulo(module_id):
                module.concluido.connect(self.on_step_done)
                self.instantiated_modules.append(module)
                self.workspace.adicionar_modulo(module_id, module)
        self.workspace.blockSignals(False)

    def sync_module(self):
        active = self.workspace.get_modulo_ativo()
        if not active or not self.current_patient_path: return

        active.pasta_paciente = self.current_patient_path
        valid, msg = active.verificar_pre_requisitos()

        if valid:
            active.inicializar(self.current_patient_path)
        elif "registration" not in active.__class__.__name__.lower():
            QtWidgets.QMessageBox.warning(self, tr("common.missing_data"), msg)

    def on_step_done(self):
        if sender := self.sender():
            if getattr(sender, 'pasta_paciente', None):
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