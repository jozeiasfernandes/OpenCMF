from typing import Optional, Any
from PySide6 import QtCore, QtWidgets

# Patient
from core.application.patient.patient_config_manager import PatientConfigManager

# Project
from core.application.patient.patient_manager import PatientManager
from core.application.home_page.project_manager.project_service import ProjectServiceHomePage
from core.settings.paths.list_paths import PATIENTS_DIR

# Flows
from application.flows.flow_service import FlowService
from core.application.flows.flow_card import FlowsCard
from core.settings.paths.list_paths import FLOWS_DIR, REGISTRATION_FLOW_NAME

# Settings
from core.settings.settings_app_manager import settings
from core.settings.icons.icon_manager import IconManager
from core.settings.localization.translator import tr

# Home Page Extras
from core.application.home_page.extras.credits_screen import Janela_Creditos
from core.application.home_page.project_manager.project_list_formatter import create_project_card, format_and_add_to_list

# Logs
import logging
from core.settings.logs.logger_manager import home_page_logger, HomePageDebugLogger, Patient_Logger
from core.settings.logs.log_monitor_window import LogMonitorWindow

logger = logging.getLogger("OpenCMF.HomePage")


class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class Home_page(QtWidgets.QWidget):
    fluxo_escolhido = QtCore.Signal(str)
    editor_solicitado = QtCore.Signal()
    config_solicitada = QtCore.Signal()

    def __init__(self, patient_manager: Optional[PatientManager] = None):
        super().__init__()
        self.debug_logger = HomePageDebugLogger()
        self.is_grid_view = False

        self.project_service = ProjectServiceHomePage(PATIENTS_DIR)
        self.flow_service = FlowService(FLOWS_DIR)

        if patient_manager:
            self.patient_manager = patient_manager
        else:
            self.config_manager = PatientConfigManager()
            self.patient_manager = PatientManager(config_manager=self.config_manager)

        self.init_ui()
        self.refresh_projects()
        self.refresh_flows()

        QtCore.QTimer.singleShot(0, self._connect_theme_signal)
        home_page_logger.info("Home_page inicializada com sucesso.")
        self.patient_logger = Patient_Logger(self.patient_manager)

    # ==========================================================================
    # UI INITIALIZATION
    # ==========================================================================
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 50, 10, 10)
        layout.setSpacing(10)

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_projects_section())
        layout.addWidget(self._build_flows_section())

    def _build_header(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        open_credits = lambda: Janela_Creditos(self).exec()
        open_logs = self._open_log_monitor

        self.btn_logo = QtWidgets.QToolButton()
        self.btn_logo.setObjectName("HeaderToolButton")
        self.btn_logo.setFixedSize(24, 24)
        self.btn_logo.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_logo.setAutoRaise(True)
        self.btn_logo.setIconSize(QtCore.QSize(24, 24))
        self.btn_logo.clicked.connect(open_credits)

        self.lbl_title = ClickableLabel("OpenCMF")
        self.lbl_title.setObjectName("AppTitleLabel")
        self.lbl_title.setCursor(QtCore.Qt.PointingHandCursor)
        self.lbl_title.clicked.connect(open_credits)

        self.btn_logs = QtWidgets.QToolButton()
        self.btn_logs.setObjectName("HeaderToolButton")
        self.btn_logs.setFixedSize(24, 24)
        self.btn_logs.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_logs.setAutoRaise(True)
        self.btn_logs.setIconSize(QtCore.QSize(24, 24))
        self.btn_logs.clicked.connect(open_logs)
        self.btn_logs.setToolTip(tr("logs.monitor_title", "Monitor de Logs"))

        self.btn_settings = QtWidgets.QToolButton()
        self.btn_settings.setObjectName("HeaderToolButton")
        self.btn_settings.setFixedSize(24, 24)
        self.btn_settings.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_settings.setAutoRaise(True)
        self.btn_settings.setIconSize(QtCore.QSize(24, 24))
        self.btn_settings.clicked.connect(self.config_solicitada.emit)

        layout.addWidget(self.btn_logo)
        layout.addSpacing(10)
        layout.addWidget(self.lbl_title)
        layout.addStretch()
        layout.addWidget(self.btn_logs)
        layout.addSpacing(10)
        layout.addWidget(self.btn_settings)
        return panel

    def _build_projects_section(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(panel)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel(f"<h3>{tr('home.recent_projects_title')}</h3>"))
        header.addStretch()

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText(tr("home.search_placeholder") or "Buscar...")
        self.search_input.setFixedWidth(200)
        self.search_input.hide()
        self.search_input.textChanged.connect(self._filter_projects)
        header.addWidget(self.search_input)

        self.btn_new_project = QtWidgets.QPushButton(tr("home.new_project_button"))
        self.btn_new_project.setFixedSize(150, 35)
        self.btn_new_project.clicked.connect(lambda: self._on_new_project_clicked())

        self.btn_remove_project = QtWidgets.QPushButton(tr("common.delete_project"))
        self.btn_remove_project.setFixedSize(150, 35)
        self.btn_remove_project.clicked.connect(self._on_remove_clicked)

        self.btn_toggle_view = QtWidgets.QPushButton()
        self.btn_toggle_view.setFixedSize(35, 35)
        self.btn_toggle_view.setIcon(IconManager.get_instance().get_icon("grid"))
        self.btn_toggle_view.clicked.connect(self._toggle_view_mode)

        self.btn_search = QtWidgets.QPushButton()
        self.btn_search.setFixedSize(35, 35)
        self.btn_search.setIcon(IconManager.get_instance().get_icon("search"))
        self.btn_search.clicked.connect(self._toggle_search)

        header.addWidget(self.btn_new_project)
        header.addWidget(self.btn_remove_project)
        header.addWidget(self.btn_search)
        header.addWidget(self.btn_toggle_view)

        self.view_container = QtWidgets.QStackedWidget()
        self.projects_view = QtWidgets.QListWidget()
        self.projects_view.setMinimumHeight(150)
        self.projects_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.projects_view.customContextMenuRequested.connect(self._show_context_menu)
        self.projects_view.itemDoubleClicked.connect(self._open_selected_project_item)
        self.view_container.addWidget(self.projects_view)

        self.grid_scroll = QtWidgets.QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.grid_scroll.setWidget(self.grid_container)
        self.view_container.addWidget(self.grid_scroll)

        layout.addLayout(header)
        layout.addWidget(self.view_container)
        return panel

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

    # ==========================================================================
    # PROJECT MANAGEMENT
    # ==========================================================================
    def refresh_projects(self):
        projects = self.project_service.list_recent_projects()

        # Evita log duplicado se chamado várias vezes em menos de 1 segundo
        import time
        current_time = time.time()
        if not hasattr(self, "_last_refresh_time") or (current_time - self._last_refresh_time) > 1.0:
            self._last_refresh_time = current_time
            self.debug_logger.info(f"Total de projetos recentes carregados: {len(projects)}")

        self.projects_view.clear()
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for idx, data in enumerate(projects):
            path = data.get("_path")
            if not path:
                continue
            if self.is_grid_view:
                card = create_project_card(data)
                card.clicked.connect(lambda p=path: self._select_patient(p))
                self.grid_layout.addWidget(card, idx // 4, idx % 4)
            else:
                item = format_and_add_to_list(self.projects_view, data)
                if item:
                    item.setData(QtCore.Qt.UserRole, path)

    def _toggle_view_mode(self):
        self.is_grid_view = not self.is_grid_view
        icon_name = "menu" if self.is_grid_view else "grid"
        self.btn_toggle_view.setIcon(IconManager.get_instance().get_icon(icon_name))
        self.view_container.setCurrentIndex(1 if self.is_grid_view else 0)
        self.update_icons()
        self.refresh_projects()

    def _filter_projects(self, text):
        text = text.lower()
        for i in range(self.projects_view.count()):
            item = self.projects_view.item(i)
            widget = self.projects_view.itemWidget(item)
            if widget and hasattr(widget, 'data'):
                nome_paciente = widget.data.get("paciente", {}).get("nome", "").lower()
                item.setHidden(text not in nome_paciente)
            else:
                item.setHidden(text not in item.text().lower())

    def _toggle_search(self):
        is_visible = self.search_input.isVisible()
        self.search_input.setVisible(not is_visible)
        if not is_visible:
            self.search_input.setFocus()
        else:
            self.search_input.clear()

    # ==========================================================================
    # FLOW MANAGEMENT
    # ==========================================================================
    def refresh_flows(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        for data in self.flow_service.list_flows(exclude_file=REGISTRATION_FLOW_NAME):
            if path := data.get("_file_path"):
                card = FlowsCard(data, path)
                card.clicked.connect(lambda p=path: self._on_flow_selected(p))
                self.cards_layout.addWidget(card)
        self.cards_layout.addStretch()

    # ==========================================================================
    # EVENTS & INTERACTION HANDLERS
    # ==========================================================================
    def _on_new_project_clicked(self):
        registration_flow = str(FLOWS_DIR / REGISTRATION_FLOW_NAME)
        self.fluxo_escolhido.emit(registration_flow)

    def _on_flow_selected(self, flow_path: str):
        if not self.patient_manager.current_path:
            QtWidgets.QMessageBox.warning(self, tr("common.warning", "Aviso"), tr("home.select_patient_first_msg",
                                                                                  "Por favor, selecione um paciente primeiro."))
            return

        import time
        current_time = time.time()
        if hasattr(self, "_last_flow_time") and (current_time - self._last_flow_time) < 1.0:
            return
        self._last_flow_time = current_time

        self.debug_logger.info("Fluxo selecionado com paciente ativo. Carregando Workspace.")
        self.fluxo_escolhido.emit(flow_path)

    def _show_context_menu(self, position):
        if item := self.projects_view.itemAt(position):
            menu = QtWidgets.QMenu(self)
            menu.addAction(tr("common.open_project"), lambda: self._select_patient_from_item(item))
            menu.addAction(tr("common.delete_project"), lambda: self._on_delete_project_requested(item))
            menu.exec(self.projects_view.mapToGlobal(position))

    def _open_selected_project_item(self, item):
        if path := item.data(QtCore.Qt.UserRole):
            self._select_patient(path)

    def _select_patient_from_item(self, item):
        if path := item.data(QtCore.Qt.UserRole):
            self._select_patient(path)

    def _select_patient(self, patient_path: str):
        import time
        current_time = time.time()

        if getattr(self, "_last_selected_path", None) == patient_path and hasattr(self, "_last_select_time") and (
                current_time - self._last_select_time) < 1.0:
            return

        self._last_select_time = current_time
        self._last_selected_path = patient_path

        self.patient_manager.set_active_patient(patient_path)
        if hasattr(self, "patient_logger") and self.patient_logger:
            self.patient_logger.log_full_state()

        # Garante que o log de debug só ocorra uma única vez por seleção real
        if not getattr(self, "_logged_patient_path", None) == patient_path:
            self._logged_patient_path = patient_path
            self.debug_logger.info("Paciente selecionado e carregado na sessão. Aguardando escolha do fluxo.",
                                   patient_path=patient_path)

    def _on_remove_clicked(self):
        if item := self.projects_view.currentItem():
            self._on_delete_project_requested(item)
        else:
            QtWidgets.QMessageBox.warning(self, tr("common.warning"), tr("home.select_project_msg"))

    def _on_delete_project_requested(self, item):
        path = item.data(QtCore.Qt.UserRole)
        if not path: return
        confirm = QtWidgets.QMessageBox.question(self, tr("home.confirm_deletion_title"),
                                                 tr("home.confirm_deletion_message"),
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                 QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            if self.project_service.remove_project(path):
                self.refresh_projects()

    # ==========================================================================
    # UTILS & SYSTEM
    # ==========================================================================
    def update_icons(self):
        theme = settings.tema
        manager = IconManager.get_instance()
        cor_default = manager.get_color(theme, "status", "default")
        self.btn_logo.setIcon(manager.get_icon("cmf", color=cor_default, size=40))
        self.btn_logs.setIcon(manager.get_icon("terminal", color=cor_default, size=24))
        self.btn_settings.setIcon(manager.get_icon("config", color=cor_default, size=24))
        icon_view = "menu" if self.is_grid_view else "grid"
        self.btn_toggle_view.setIcon(manager.get_icon(icon_view, color=cor_default, size=24))
        self.btn_search.setIcon(manager.get_icon("search", color=cor_default, size=24))

    def _connect_theme_signal(self):
        if self.window() and hasattr(self.window(), 'theme_changed'):
            self.window().theme_changed.connect(self.update_icons)
            self.update_icons()
        else:
            QtCore.QTimer.singleShot(500, self._connect_theme_signal)

    def update_list(self):
        self.refresh_projects()
        self.refresh_flows()

    def _open_log_monitor(self):
        if not hasattr(self, "log_window") or self.log_window is None:
            self.log_window = LogMonitorWindow(self)
        self.log_window.show()
        self.log_window.raise_()
        self.log_window.activateWindow()