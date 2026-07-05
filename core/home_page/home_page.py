from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path
import sys

from core import settings, IconManager, tr, ProjectServiceHomePage, FlowServiceHomePage

from core.home_page.extras.tela_creditos import Janela_Creditos
from core.home_page.flow.fluxo_card import FluxoCard
from core.home_page.managers.project_list_formatter import format_and_add_to_list


def get_project_root():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


BASE_DIR = get_project_root()
PATIENTS_DIR = BASE_DIR / "patients"
FLOWS_DIR = BASE_DIR / "flows"
ICONS_DIR = BASE_DIR / "appearance" / "icons"
REGISTRATION_FLOW_NAME = "new_patient_registration.json"


class Home_page(QtWidgets.QWidget):
    projeto_selecionado = QtCore.Signal(str, str)
    fluxo_escolhido = QtCore.Signal(str)
    editor_solicitado = QtCore.Signal()
    config_solicitada = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.project_service = ProjectServiceHomePage(PATIENTS_DIR)
        self.flow_service = FlowServiceHomePage(FLOWS_DIR)
        self.init_ui()
        self.update_list()
        QtCore.QTimer.singleShot(0, self._connect_theme_signal)

    def _connect_theme_signal(self):
        if hasattr(self.window(), 'theme_changed'):
            self.window().theme_changed.connect(self.update_icons)
            self.update_icons()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 50, 10, 10)
        layout.setSpacing(10)

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_projects_section())
        layout.addWidget(self._build_flows_section())

    def update_icons(self):
        theme = settings.get("preferencias", "tema", "dark")
        manager = IconManager.get_instance()

        cor_default = manager.get_color(theme, "status", "default")

        self.btn_logo.setIcon(manager.get_icon("OpenCFM_Logo", color=cor_default, size=40))
        self.btn_settings.setIcon(manager.get_icon("config", color=cor_default, size=24))

    def update_list(self):
        self.refresh_projects()
        self.refresh_flows()

    def _build_header(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Configuração do botão de Logo
        self.btn_logo = QtWidgets.QPushButton()
        self.btn_logo.setFixedSize(120, 40)
        self.btn_logo.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_logo.setIconSize(QtCore.QSize(110, 40))
        self.btn_logo.clicked.connect(lambda: Janela_Creditos(self).exec())

        # Configuração do botão de Settings
        self.btn_settings = QtWidgets.QPushButton()
        self.btn_settings.setFixedSize(40, 40)
        self.btn_settings.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_settings.setIconSize(QtCore.QSize(24, 24))
        self.btn_settings.clicked.connect(self.config_solicitada.emit)

        # Adiciona efeitos simples de estilo para melhorar a interação (opcional)
        self.btn_logo.setStyleSheet("QPushButton { border: none; }")
        self.btn_settings.setStyleSheet("QPushButton { border: none; }")

        layout.addWidget(self.btn_logo)
        layout.addStretch()
        layout.addWidget(self.btn_settings)
        return panel

    def _build_projects_section(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(panel)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel(f"<h3>{tr('home.recent_projects_title')}</h3>"))
        header.addStretch()

        # --- Campo de busca (oculto por padrão) ---
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText(tr("home.search_placeholder") or "Buscar...")
        self.search_input.setFixedWidth(200)
        self.search_input.hide()
        self.search_input.textChanged.connect(self._filter_projects)
        header.addWidget(self.search_input)

        # --- Botão de busca (após o btn_remove_project na lógica de UI) ---
        self.btn_new_project = QtWidgets.QPushButton(tr("home.new_project_button"))
        self.btn_new_project.setFixedSize(150, 35)
        self.btn_new_project.clicked.connect(
            lambda: self.fluxo_escolhido.emit(str(FLOWS_DIR / REGISTRATION_FLOW_NAME))
        )

        self.btn_remove_project = QtWidgets.QPushButton(tr("common.delete_project"))
        self.btn_remove_project.setFixedSize(150, 35)
        self.btn_remove_project.clicked.connect(self._on_remove_clicked)

        self.btn_search = QtWidgets.QPushButton()
        self.btn_search.setFixedSize(35, 35)
        self.btn_search.setIcon(IconManager.get_instance().get_icon("search"))
        self.btn_search.clicked.connect(self._toggle_search)

        # Adicionando ao layout
        header.addWidget(self.btn_new_project)
        header.addWidget(self.btn_remove_project)
        header.addWidget(self.btn_search)

        self.projects_view = QtWidgets.QListWidget()
        self.projects_view.setMinimumHeight(150)
        self.projects_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.projects_view.customContextMenuRequested.connect(self._show_context_menu)
        self.projects_view.itemDoubleClicked.connect(self._open_selected_project)

        layout.addLayout(header)
        layout.addWidget(self.projects_view)
        return panel

    def _toggle_search(self):
        is_visible = self.search_input.isVisible()
        self.search_input.setVisible(not is_visible)
        if not is_visible:
            self.search_input.setFocus()
        else:
            self.search_input.clear()  # Limpa ao fechar

    def _filter_projects(self, text):
        text = text.lower()
        for i in range(self.projects_view.count()):
            item = self.projects_view.item(i)
            widget = self.projects_view.itemWidget(item)

            nome_paciente = widget.data.get("paciente", {}).get("nome", "").lower()

            item.setHidden(text not in nome_paciente)

    def _build_flows_section(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(panel)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel(f"<h3>{tr('home.available_flows_title')}</h3>"))
        header.addStretch()

        self.btn_new_flow = QtWidgets.QPushButton(tr("home.new_flow_button"))
        self.btn_new_flow.setFixedSize(150, 35)
        self.btn_new_flow.clicked.connect(self.editor_solicitado.emit)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QVBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(QtCore.Qt.AlignTop)
        scroll.setWidget(self.cards_container)

        header.addWidget(self.btn_new_flow)
        layout.addLayout(header)
        layout.addWidget(scroll)
        return panel

    def refresh_projects(self):
        self.projects_view.clear()
        for data in self.project_service.list_recent_projects():
            if path := data.get("_path"):
                item = format_and_add_to_list(self.projects_view, data)
                if item:
                    item.setData(QtCore.Qt.UserRole, path)

    def refresh_flows(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        for data in self.flow_service.list_flows(exclude_file=REGISTRATION_FLOW_NAME):
            if path := data.get("_file_path"):
                card = FluxoCard(data, path)
                card.clicado.connect(self.fluxo_escolhido.emit)
                self.cards_layout.addWidget(card)
        self.cards_layout.addStretch()

    def _open_selected_project(self, item):
        if path := item.data(QtCore.Qt.UserRole):
            self.projeto_selecionado.emit(path, "open")

    def _show_context_menu(self, position):
        if item := self.projects_view.itemAt(position):
            menu = QtWidgets.QMenu(self)
            menu.addAction(tr("common.open_project"), lambda: self._open_selected_project(item))
            menu.addAction(tr("common.delete_project"), lambda: self._on_delete_project_requested(item))
            menu.exec(self.projects_view.mapToGlobal(position))

    def _on_remove_clicked(self):
        if item := self.projects_view.currentItem():
            self._on_delete_project_requested(item)
        else:
            QtWidgets.QMessageBox.warning(self, tr("common.warning"), tr("home.select_project_msg"))

    def _on_delete_project_requested(self, item):
        path = item.data(QtCore.Qt.UserRole)
        if not path: return

        confirm = QtWidgets.QMessageBox.question(
            self, tr("home.confirm_deletion_title"), tr("home.confirm_deletion_message"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )

        if confirm == QtWidgets.QMessageBox.Yes:
            if self.project_service.remove_project(path):
                self.refresh_projects()