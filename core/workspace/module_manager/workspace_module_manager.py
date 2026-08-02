import logging
from typing import Optional
from PySide6 import QtWidgets, QtCore

# Modules
from core.workspace.module_manager.tab_controller import TabController
from core.workspace.module_manager.workspace_modules_mixin import WorkspaceModulesMixin

# Models
from core.workspace.models.contracts import IModule

# Settings
logger = logging.getLogger("OpenCMF.Workspace.ModuleManager")


class WorkspaceModuleManager(QtCore.QObject, WorkspaceModulesMixin):
    """Gerencia de forma unificada o sistema de abas e o ciclo de vida dos módulos do workspace."""

    # Sinais para desacoplar a comunicação com a janela principal
    module_opened = QtCore.Signal(str)
    module_closed = QtCore.Signal(int)

    def __init__(
        self,
        container: QtWidgets.QStackedWidget,
        registry,
        toolbar_manager,
        side_manager,
        central_manager,
        status_bar_manager: Optional[QtWidgets.QStatusBar] = None,
        parent: Optional[QtCore.QObject] = None,
    ):
        super().__init__(parent)
        self.registry = registry
        self.toolbar_manager = toolbar_manager
        self.side_manager = side_manager
        self.central_manager = central_manager
        self.status_bar_manager = status_bar_manager

        # Controlador de abas visual e de navegação
        self.tab_controller = TabController(container)

        # Conecta os sinais do TabController aos comportamentos do gerenciador
        self.tab_controller.tab_changed.connect(self._handle_tab_changed)
        self.tab_controller.tab_closed.connect(self._handle_tab_closed)

    def load_modules(self):
        """Carrega e instancia todos os módulos ativos do registry na barra de abas."""
        try:
            if not hasattr(self.registry, "list_active_modules"):
                return

            active_module_ids = self.registry.list_active_modules()
            for module_id in active_module_ids:
                # Obtém ou instancia o módulo através do registro
                if hasattr(self.registry, "get_or_create_module"):
                    module_instance = self.registry.get_or_create_module(module_id)
                elif hasattr(self.registry, "get_module"):
                    module_instance = self.registry.get_module(module_id)
                else:
                    module_instance = None

                if module_instance:
                    # Correção: alinhado com as propriedades e métodos do IModule ('nome' e 'get_central_area')
                    title = getattr(module_instance, "nome", None) or getattr(module_instance, "name", module_id)

                    widget = None
                    if hasattr(module_instance, "get_central_area") and callable(module_instance.get_central_area):
                        widget = module_instance.get_central_area()
                    elif hasattr(module_instance, "central_widget"):
                        widget = module_instance.central_widget
                    elif hasattr(module_instance, "widget"):
                        widget = module_instance.widget

                    if widget:
                        self.open_module_tab(module_id, title, widget)
        except Exception as e:
            logger.error(f"Erro ao carregar os módulos no manager: {e}")

    @property
    def tab_bar_layout(self) -> QtWidgets.QHBoxLayout:
        """Expõe o layout da barra de abas para inserção na UI principal."""
        return self.tab_controller.tab_bar_layout

    def open_module_tab(self, module_id: str, title: str, content_widget: QtWidgets.QWidget):
        """Apenas adiciona uma nova aba para o módulo sem forçar a ativação imediata."""
        self.tab_controller.add_tab(title, content_widget)
        self.module_opened.emit(module_id)

    def _handle_tab_changed(self, index: int):
        """Disparado quando o usuário troca de aba visualmente."""
        try:
            active_modules = self.registry.list_active_modules()
            if 0 <= index < len(active_modules):
                module_id = active_modules[index]
                # Dispara o método de troca de módulo do mixin/manager
                if hasattr(self, "on_module_changed"):
                    self.on_module_changed(module_id)
        except Exception as e:
            logger.error(f"Erro ao tratar mudança de aba no index {index}: {e}")

    def _handle_tab_closed(self, index: int):
        """Disparado quando uma aba é fechada pelo usuário."""
        self.module_closed.emit(index)
        # Se não houver mais abas, limpa o workspace atual
        if not self.tab_controller.tabs:
            from core.workspace.layout.layout import ModuleDistributor
            ModuleDistributor.cleanup(
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

    def get_modulo_ativo(self) -> Optional[IModule]:
        """Retorna o módulo ativo consultando o TabController e o Registry."""
        try:
            current_index = self.tab_controller.container.currentIndex()
            if current_index >= 0:
                active_modules = self.registry.list_active_modules()
                if current_index < len(active_modules):
                    module_id = active_modules[current_index]
                    # Usa o método correto do registry (ex: get_or_create_module)
                    if hasattr(self.registry, "get_or_create_module"):
                        return self.registry.get_or_create_module(module_id)
        except Exception as e:
            logger.error(f"Erro ao obter módulo ativo no manager: {e}")
        return None