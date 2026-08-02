import logging
from typing import Any, Optional
from PySide6 import QtCore, QtWidgets

from core.workspace.containers.central_area_container.central_area_manager import CentralAreaManager
from core.workspace.containers.header_container.header_panel import HeaderPanel
from module_manager.workspace_modules_mixin import WorkspaceModulesMixin
from core.workspace.containers.side_panel_container.side_panel_manager import SidePanelManager
from core.workspace.containers.status_bar.status_bar import StatusBarManager
from core.workspace.containers.toolbar_container.toolbar_manager import ToolbarManager
from core.workspace.containers.side_panel_container.side_panel_container import SidePanelContainer

from core.workspace.models.registry import WorkspaceRegistry
from core.workspace.patient.state import WorkspaceState
from core.workspace.patient.workspace_patient import WorkspacePatientMixin
from core.workspace.layout.workspace_loaders_components import WorkspaceComponentHandler
from core.settings.logs.archives.workspace_log import Workspace_Logger
from settings.settings_app_manager import settings

from settings.logs.archives.containers import container

logger = logging.getLogger("OpenCMF.Workspace")


class WorkspaceManager(QtWidgets.QWidget, WorkspaceModulesMixin, WorkspacePatientMixin):
    """Gerencia o layout principal do workspace e a integração entre componentes."""

    MIN_CENTRAL_WIDTH = 200
    DEFAULT_STRETCH_FACTORS = [4, 1]

    def __init__(self, context: Optional[Any] = None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # Debug/Inspeção dos containers acoplada à inicialização da Workspace
        containers_logger = container.containers_logger()
        state_info = containers_logger.inspect_container_state(container)
        containers_logger.info(
            f"Container inspecionado via Workspace. Provedores ativos: {state_info.get('providers', [])}",
            container_name="ApplicationContainer"
        )

        self.context = context
        self.state = WorkspaceState()
        self.registry = WorkspaceRegistry()

        self.current_patient_path = ""
        self.component_handler = WorkspaceComponentHandler(self)

        # Instancia o logger/inspetor passando a referência do workspace
        self.debug_inspector = Workspace_Logger(self)

        self._setup_layout()
        self._setup_components()
        self._configure_splitter()

    def _setup_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def _setup_components(self):
        self.header = HeaderPanel(workspace_manager=self)
        self.main_layout.addWidget(self.header)

        self.toolbar_manager = ToolbarManager()
        self.main_layout.addWidget(self.toolbar_manager.top_container)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # 1. Adiciona a área central (ficará à esquerda)
        self.central_manager = CentralAreaManager(self)
        self.splitter.addWidget(self.central_manager.get_container())

        # 2. Instancia o gerenciador do painel lateral
        self.side_manager = SidePanelManager(self)

        if hasattr(self.side_manager, "container") and self.side_manager.container:
            if hasattr(self.side_manager.container, "toggle_requested"):
                self.side_manager.container.toggle_requested.connect(self.notificar_toggle_side_panel)

        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")
        if current_mode != "floating":
            self.side_manager.container.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            self.splitter.addWidget(self.side_manager.container)
            self.splitter.setStretchFactor(0, 7)
            self.splitter.setStretchFactor(1, 3)
        else:
            # No modo flutuante, a área central ocupa 100% do splitter
            self.splitter.setStretchFactor(0, 1)

        self.main_layout.addWidget(self.splitter, stretch=1)
        self.main_layout.addWidget(self.toolbar_manager.bottom_container)

        self.status_bar_manager = StatusBarManager()
        self.main_layout.addWidget(self.status_bar_manager)


        try:
            containers_logger = container.containers_logger()
            if hasattr(self.side_manager, "container") and self.side_manager.container:
                containers_logger.inspect_side_panel_widgets(self.side_manager.container, container_name="SidePanelDiagnostic")
        except Exception as e:
            logger.error(f"Erro ao rodar diagnóstico do side panel: {e}")

    def _configure_splitter(self):
        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")

        if current_mode == "floating":
            self.splitter.setCollapsible(0, False)
            self.splitter.setStretchFactor(0, 1)
            return

        # Permite que o painel lateral possa ser recolhido
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)
        self.splitter.setChildrenCollapsible(True)

        self.splitter.setStretchFactor(0, 7)
        self.splitter.setStretchFactor(1, 3)

    def notificar_toggle_side_panel(self, colapsado: bool):
        """Método unificado chamado pelo cabeçalho do side panel para atualizar o layout, redimensionar e refrescar as vistas."""
        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")
        if current_mode == "floating":
            return

        if hasattr(self, "splitter") and self.splitter:
            sizes = self.splitter.sizes()
            total = sum(sizes)
            if total > 0:
                if colapsado:
                    # Recolhe o painel lateral mantendo apenas a aba visível (ex: 40 pixels)
                    self.splitter.setSizes([total - 40, 40])
                else:
                    # Restaura o tamanho padrão proporcional (70% / 30%)
                    central_width = int(total * 0.70)
                    side_width = total - central_width
                    if central_width < self.MIN_CENTRAL_WIDTH:
                        central_width = self.MIN_CENTRAL_WIDTH
                        side_width = total - self.MIN_CENTRAL_WIDTH
                    self.splitter.setSizes([central_width, side_width])

            self.splitter.update()
            self.splitter.repaint()

        if hasattr(self, "central_manager") and hasattr(self.central_manager, "get_container"):
            container = self.central_manager.get_container()
            if container:
                container.update()
                container.repaint()

    def _apply_initial_splitter_sizes(self):
        """Aplica os tamanhos iniciais do splitter garantindo que a área central não fique com largura 0."""
        if not self.splitter or not self.splitter.isVisible():
            return

        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")
        if current_mode == "floating":
            self.splitter.setSizes([self.splitter.width(), 0])
            return

        total_width = self.splitter.width()
        if total_width > 0:
            central_width = int(total_width * 0.70)
            side_width = total_width - central_width
            # Garante o mínimo de espaço para a área central evitar o colapso visual
            if central_width < self.MIN_CENTRAL_WIDTH:
                central_width = self.MIN_CENTRAL_WIDTH
                side_width = total_width - self.MIN_CENTRAL_WIDTH
            self.splitter.setSizes([central_width, side_width])
        else:
            self.splitter.setSizes([700, 300])

    def abrir_seletor_componentes(self):
        logger.info("Solicitação para abrir o seletor de componentes.")
        self.component_handler.abrir_seletor()

    def log_debug_state(self, level: int = logging.INFO):
        """Dispara a inspeção e registro do estado atual através do Workspace_Logger."""
        if hasattr(self, "debug_inspector") and self.debug_inspector:
            self.debug_inspector.log_full_state(level=level)

    def reset_workspace(self):
        logger.info("Iniciando o reset completo do workspace.")
        self.registry.clear_all()
        self.header.clear_tabs()
        self.toolbar_manager.clear_all()

        if hasattr(self.side_manager, 'clear_all'):
            self.side_manager.clear_all()

        self.central_manager.clear()
        logger.debug(f"Estado atual pós-reset - Módulos ativos: {self.registry.list_active_modules()}")

    def reconstruir_side_panel(self):
        """Reconstrói dinamicamente o container do painel lateral com base no novo modo (settings_page_tabs ou floating)."""
        if not hasattr(self, "side_manager") or not self.side_manager:
            return

        # 1. Preserva os painéis ativos no container atual para reutilizá-los
        current_panels = {}
        old_container = getattr(self.side_manager, "container", None)

        if old_container:
            if hasattr(old_container, "panels"):
                current_panels = dict(old_container.panels)

            # Se estava em modo floating, fecha a janela antiga de forma segura
            if getattr(old_container, "current_mode", "") == "floating" and hasattr(old_container, "floating_window"):
                if old_container.floating_window:
                    old_container.floating_window.close()

            # Remove o container antigo do layout/splitter de forma segura
            old_container.setParent(None)
            old_container.deleteLater()

        # 2. Instancia um novo container e atualiza a referência no gerenciador
        new_container = SidePanelContainer(title="Side Panel", workspace_manager=self, parent=self)
        self.side_manager.container = new_container

        # Conecta o sinal de toggle do novo container reconstruído ao WorkspaceManager
        if hasattr(new_container, "toggle_requested"):
            new_container.toggle_requested.connect(self.notificar_toggle_side_panel)

        # 3. Reinsere no QSplitter principal do workspace
        current_mode = getattr(settings, "side_panel_mode", "settings_page_tabs")
        if current_mode != "floating":
            new_container.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            self.splitter.addWidget(new_container)
            self.splitter.setStretchFactor(0, 7)
            self.splitter.setStretchFactor(1, 3)
            new_container.setVisible(True)
        else:
            # No modo flutuante, o container principal permanece oculto e o splitter ajusta para a área central
            new_container.setVisible(False)
            self.splitter.setStretchFactor(0, 1)

        # 4. Restaura os painéis abertos no novo container usando o método nativo do container
        if current_panels:
            new_container.panels = current_panels
            if hasattr(new_container, "reattach_panels_to_new_container"):
                new_container.reattach_panels_to_new_container(new_container)

        # 5. Reaplica as configurações visuais do splitter e recalcula os tamanhos iniciais
        self._configure_splitter()
        self._apply_initial_splitter_sizes()
        self.splitter.update()
        self.splitter.repaint()

    def reattach_panels_to_new_container(self, new_container):
        """Reanexa os painéis em cache para o novo container, evitando reparenting redundante."""
        for panel_id, panel in list(self.panels.items()):
            title = self.panel_titles.get(panel_id, panel_id.replace("_", " ").title())

            # Se o painel possui método próprio de reattach, delega e evita add_panel duplicado
            if hasattr(panel, "reattach") and callable(panel.reattach):
                panel.reattach(new_container)

            # Caso contrário, adiciona diretamente ao novo container
            elif new_container and hasattr(new_container, "add_panel"):
                new_container.add_panel(panel_id, panel, title)

            if panel:
                panel.setVisible(True)

    def showEvent(self, event):
        """Garante que os tamanhos do splitter sejam aplicados assim que a janela for exibida e tiver largura real."""
        super().showEvent(event)
        QtCore.QTimer.singleShot(50, self._apply_initial_splitter_sizes)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    workspace = WorkspaceManager()
    workspace.setWindowTitle("Teste de WorkspaceManager")
    workspace.resize(1280, 720)

    workspace.show()

    QtCore.QTimer.singleShot(500, workspace.log_debug_state)

    sys.exit(app.exec())