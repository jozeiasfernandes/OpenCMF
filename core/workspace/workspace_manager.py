import sys
import logging
from typing import Optional, Any

from PySide6 import QtWidgets, QtCore

from core.workspace.contracts import IModule
from core.workspace.header_container.header_panel import HeaderPanel
from core.workspace.toolbar_container.toolbar_manager import ToolbarManager
from core.workspace.side_panel_container.side_panel_manager import SidePanelManager
from core.workspace.central_area_container.central_area_manager import CentralAreaManager
from core.workspace.layout import ModuleDistributor
from core.workspace.registry import WorkspaceRegistry
from core.workspace.status_bar.status_bar import StatusBarManager
from core.workspace.state import WorkspaceState
from core.workspace.workspace_loaders_components import WorkspaceComponentHandler

logger = logging.getLogger("OpenCMF.Workspace")


class WorkspaceManager(QtWidgets.QWidget):
    """Gerencia o layout principal do workspace e a integração entre componentes."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = WorkspaceState()
        self.registry = WorkspaceRegistry()

        # Inicializa o controle de caminho do paciente
        self.current_patient_path = ""

        # Inicializa o handler de componentes dinâmicos (Components_List)
        self.component_handler = WorkspaceComponentHandler(self)

        self._setup_layout()
        self._setup_components()
        self._configure_splitter()

    def _setup_layout(self):
        """Configura o layout principal vertical."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def _setup_components(self):
        """Inicializa e adiciona todos os componentes visuais."""
        # Header
        self.header = HeaderPanel()
        self.main_layout.addWidget(self.header)

        # Toolbar Manager
        self.toolbar_manager = ToolbarManager()
        self.main_layout.addWidget(self.toolbar_manager.top_container)

        # Splitter (Central + Side Panel)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        self.central_manager = CentralAreaManager(self)
        self.splitter.addWidget(self.central_manager.get_container())

        self.side_manager = SidePanelManager(self)
        self.side_manager.container.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Expanding
        )
        self.splitter.addWidget(self.side_manager.container)

        self.main_layout.addWidget(self.splitter, stretch=1)

        # Toolbar inferior + Status Bar
        self.main_layout.addWidget(self.toolbar_manager.bottom_container)

        self.status_bar_manager = StatusBarManager()
        self.main_layout.addWidget(self.status_bar_manager)

        # Ajuste inicial do splitter
        QtCore.QTimer.singleShot(100, lambda: self.splitter.setSizes([900, 300]))

    def _configure_splitter(self):
        """Configurações do QSplitter."""
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 1)

    # ======================= Módulos =======================

    def on_module_changed(self, module_id: str):
        """Troca o módulo ativo e distribui seus componentes."""
        try:
            # Limpeza dos containers
            ModuleDistributor.cleanup(
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            # Carrega e distribui o novo módulo
            module = self.registry.get_or_create_module(module_id)
            ModuleDistributor.distribute(
                module,
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            # Garante que o módulo recém-carregado receba o paciente atual se houver
            if self.state.current_patient and hasattr(module, "inicializar"):
                module.inicializar(self.state.current_patient)

            logger.info(f"Módulo '{module_id}' carregado com sucesso.")
            self.status_bar_manager.showMessage(f"Módulo '{module_id}' carregado.", 3000)

        except Exception as e:
            logger.error(f"Erro crítico ao carregar módulo '{module_id}': {e}", exc_info=True)
            self.status_bar_manager.showMessage("Erro ao carregar módulo", 5000)

    def get_modulo_ativo(self) -> Optional[IModule]:
        """Retorna o módulo correspondente à aba atualmente selecionada."""
        current_index = self.header.tab_bar.currentIndex()
        if current_index >= 0:
            module_id = self.header.tab_bar.tabData(current_index)
            if module_id:
                return self.registry.get_or_create_module(module_id)
        return None

    def set_patient_path(self, path: str):
        """Atualiza o caminho do paciente evitando chamadas redundantes."""
        if self.current_patient_path == path:
            return
        self.current_patient_path = path

        # Sincroniza também com o state global
        if hasattr(self, "state"):
            self.state.current_patient = path

        if modulo := self.get_modulo_ativo():
            self._safe_inicializar(modulo)

    def _safe_inicializar(self, instancia: Any):
        """Inicializa o módulo de forma segura caso o caminho seja diferente."""
        if not self.current_patient_path:
            return

        path_modulo = getattr(instancia, 'pasta_paciente', None)
        if str(path_modulo) != str(self.current_patient_path):
            if hasattr(instancia, 'inicializar'):
                instancia.inicializar(self.current_patient_path)

    # ======================= Configuração de Componentes =======================

    def abrir_seletor_componentes(self):
        """Abre a janela de listagem de componentes para customização."""
        self.component_handler.abrir_seletor()

    # ======================= Patient & Reset =======================

    def reset_workspace(self):
        """Limpa todo o workspace (módulos, abas, painéis, etc)."""
        self.registry.clear_all()
        self.header.clear_tabs()
        self.toolbar_manager.clear_all()

        # Limpeza segura do side_manager considerando o container loader
        if hasattr(self.side_manager, 'clear_all'):
            self.side_manager.clear_all()
        elif hasattr(self.side_manager.container, 'limpar'):
            self.side_manager.container.limpar()

        self.central_manager.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    workspace = WorkspaceManager()
    workspace.setWindowTitle("Teste de WorkspaceManager")
    workspace.resize(1280, 720)

    workspace.show()

    sys.exit(app.exec())