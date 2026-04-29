import sys
import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from appearance.extras.tela_creditos import Janela_Creditos
from appearance.flow.fluxo_card import FluxoCard
from core.project.project_manager import ProjectManager
from core.localization.translator import tr


def get_resource_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent.resolve()


def get_data_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent.resolve()
    return Path(__file__).parent.parent.resolve()


BASE_DIR = get_resource_path()
DATA_DIR = get_data_path()
PATIENTS_DIR = DATA_DIR / "patients"
FLOWS_DIR = BASE_DIR / "flows"
ICONS_DIR = BASE_DIR / "appearance" / "icons"

PATIENTS_DIR.mkdir(exist_ok=True)
REGISTRATION_FLOW = str(FLOWS_DIR / "new_patient_registration.json")


class Home_page(QtWidgets.QWidget):
    projeto_selecionado = QtCore.Signal(str, str)
    fluxo_escolhido = QtCore.Signal(str)
    editor_solicitado = QtCore.Signal()
    config_solicitada = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.manager = ProjectManager(PATIENTS_DIR, FLOWS_DIR)
        self.init_ui()
        self.update_list()

    def init_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 50, 10, 10)
        self.main_layout.setSpacing(10)
        self.main_layout.addWidget(self.build_header())
        self.main_layout.addWidget(self.build_projects_section())
        self.main_layout.addWidget(self.build_flows_section())

    def update_list(self):
        self.refresh_projects()
        self.refresh_flows()

    def build_header(self) -> QtWidgets.QFrame:
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_logo = QtWidgets.QPushButton()
        self.btn_logo.setFixedSize(120, 40)
        self.btn_logo.setCursor(QtCore.Qt.PointingHandCursor)

        logo_path = ICONS_DIR / "OpenCFM_Logo_Branco.png"
        if logo_path.exists():
            self.btn_logo.setIcon(QtGui.QIcon(str(logo_path)))
            self.btn_logo.setIconSize(QtCore.QSize(110, 40))
        else:
            self.btn_logo.setText("OpenCMF")
        self.btn_logo.clicked.connect(self.show_credits)

        self.btn_settings = QtWidgets.QPushButton()
        self.btn_settings.setFixedSize(40, 40)
        self.btn_settings.setCursor(QtCore.Qt.PointingHandCursor)

        settings_icon = ICONS_DIR / "config.png"
        if settings_icon.exists():
            self.btn_settings.setIcon(QtGui.QIcon(str(settings_icon)))
            self.btn_settings.setIconSize(QtCore.QSize(24, 24))
        self.btn_settings.clicked.connect(self.config_solicitada.emit)

        layout.addWidget(self.btn_logo)
        layout.addStretch()
        layout.addWidget(self.btn_settings)
        return panel

    def show_credits(self):
        self.credits_window = Janela_Creditos(self)
        self.credits_window.exec()

    def build_projects_section(self) -> QtWidgets.QFrame:
        panel = QtWidgets.QFrame()
        panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(panel)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(QtWidgets.QLabel(f"<h3>{tr('home.recent_projects_title')}</h3>"))
        header_layout.addStretch()

        self.btn_new_project = QtWidgets.QPushButton(tr("home.new_project_button"))
        self.btn_new_project.setFixedSize(150, 35)
        self.btn_new_project.clicked.connect(lambda: self.fluxo_escolhido.emit(REGISTRATION_FLOW))

        self.btn_delete_project = QtWidgets.QPushButton(tr("home.delete_button"))
        self.btn_delete_project.setFixedSize(150, 35)
        self.btn_delete_project.clicked.connect(self.on_delete_project_requested)

        header_layout.addWidget(self.btn_new_project)
        header_layout.addWidget(self.btn_delete_project)

        self.projects_view = QtWidgets.QListWidget()
        self.projects_view.setMinimumHeight(150)
        self.projects_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.projects_view.customContextMenuRequested.connect(self.show_context_menu)
        self.projects_view.itemDoubleClicked.connect(self.open_selected_project)

        layout.addLayout(header_layout)
        layout.addWidget(self.projects_view)
        return panel

    def refresh_projects(self):
        self.projects_view.clear()
        try:
            projects = self.manager.listar_projetos_recentes()
            for data in projects:
                info = data.get("paciente") or {}
                name = info.get("nome") or Path(data.get("_caminho_local", "")).name
                item = QtWidgets.QListWidgetItem(name or tr("home.unknown_patient"))
                item.setData(QtCore.Qt.UserRole, data.get("_caminho_local"))
                self.projects_view.addItem(item)
        except Exception as e:
            logging.error(f"Error listing projects: {e}")

    def open_selected_project(self, item):
        self.projeto_selecionado.emit(item.data(QtCore.Qt.UserRole), "open")

    def on_delete_project_requested(self):
        if item := self.projects_view.currentItem():
            self.confirm_project_deletion(item)
        else:
            QtWidgets.QMessageBox.warning(self, tr("common.warning"), tr("home.select_patient_msg"))

    def show_context_menu(self, position):
        if item := self.projects_view.itemAt(position):
            menu = QtWidgets.QMenu()
            open_action = menu.addAction(tr("common.open_project"))
            delete_action = menu.addAction(tr("common.delete_project"))
            delete_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))

            choice = menu.exec(self.projects_view.mapToGlobal(position))
            if choice == open_action:
                self.open_selected_project(item)
            elif choice == delete_action:
                self.confirm_project_deletion(item)

    def confirm_project_deletion(self, item):
        path = item.data(QtCore.Qt.UserRole)
        confirm = QtWidgets.QMessageBox.question(
            self, tr("home.confirm_deletion_title"),
            tr("home.confirm_deletion_message").format(item.text()),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            if self.manager.remover_projeto(path):
                self.refresh_projects()
            else:
                QtWidgets.QMessageBox.critical(self, tr("common.error"), tr("home.delete_folder_error"))

    def build_flows_section(self) -> QtWidgets.QFrame:
        panel = QtWidgets.QFrame()
        panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(panel)

        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel(f"<h3>{tr('home.available_flows_title')}</h3>"))
        header.addStretch()

        self.btn_new_flow = QtWidgets.QPushButton(tr("home.new_flow_button"))
        self.btn_new_flow.setFixedSize(150, 35)
        self.btn_new_flow.clicked.connect(self.editor_solicitado.emit)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QVBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(QtCore.Qt.AlignTop)
        self.cards_layout.setSpacing(10)

        self.scroll_area.setWidget(self.cards_container)
        header.addWidget(self.btn_new_flow)
        layout.addLayout(header)
        layout.addWidget(self.scroll_area)
        return panel

    def refresh_flows(self):
        while self.cards_layout.count():
            if child := self.cards_layout.takeAt(0).widget():
                child.deleteLater()
        try:
            flows = self.manager.listar_fluxos_disponiveis(ignorar_nome=REGISTRATION_FLOW)
            for data in flows:
                card = FluxoCard(data, data["_caminho_arquivo"])
                card.clicado.connect(self.fluxo_escolhido.emit)
                if hasattr(card, 'exclusao_solicitada'):
                    card.exclusao_solicitada.connect(self.confirm_delete_flow)
                self.cards_layout.addWidget(card)
            self.cards_layout.addStretch()
        except Exception as e:
            logging.error(f"Error listing flows: {e}")

    def confirm_delete_flow(self, file_path):
        confirm = QtWidgets.QMessageBox.question(
            self, tr("home.confirm_deletion_title"),
            f"{tr('home.delete_flow_msg')}: {Path(file_path).stem}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            if self.manager.remover_fluxo(file_path):
                self.refresh_flows()