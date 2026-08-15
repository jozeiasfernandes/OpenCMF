import logging
from typing import Optional
from PySide6 import QtWidgets, QtCore

# Modules
from core.workspace.modules.tabs.tab_controller import TabController
from core.workspace.modules.module_mixin import WorkspaceModulesMixin

# Models
from core.workspace.models.contracts import IModule

logger = logging.getLogger("OpenCMF.Workspace.ModuleManager")


class WorkspaceModuleManager(QtCore.QObject, WorkspaceModulesMixin):
    """Gerencia o sistema de abas e o ciclo de vida dos módulos do workspace."""

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

        self.tab_controller = TabController(container)
        self._widget_to_module_id: dict[QtWidgets.QWidget, str] = {}

        self.tab_controller.tab_changed.connect(self._handle_tab_changed)
        self.tab_controller.tab_closed.connect(self._handle_tab_closed)

    # =========================================================================
    # PROPERTIES
    # =========================================================================
    @property
    def tab_bar_layout(self) -> QtWidgets.QHBoxLayout:
        """Expõe o layout da barra de abas para inserção na UI principal."""
        return self.tab_controller.tab_bar_layout

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    def load_modules(self):
        """Carrega e instancia todos os módulos ativos do registry."""
        try:
            self._widget_to_module_id.clear()

            if hasattr(self.tab_controller, "clear_tabs"):
                self.tab_controller.clear_tabs()
            elif hasattr(self.tab_controller, "clear"):
                self.tab_controller.clear()
            elif hasattr(self.tab_controller, "removeAllTabs"):
                self.tab_controller.removeAllTabs()

            if hasattr(self.tab_controller, "tab_bar_layout") and self.tab_controller.tab_bar_layout:
                layout = self.tab_controller.tab_bar_layout
                while layout.count() > 0:
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                        item.widget().deleteLater()

            if not hasattr(self.registry, "list_active_modules"):
                return

            active_module_ids = self.registry.list_active_modules()
            loaded_ids = set()

            for module_id in active_module_ids:
                if module_id in loaded_ids:
                    continue
                loaded_ids.add(module_id)

                if hasattr(self.registry, "get_or_create_module"):
                    module_instance = self.registry.get_or_create_module(module_id)
                elif hasattr(self.registry, "get_module"):
                    module_instance = self.registry.get_module(module_id)
                else:
                    module_instance = None

                if module_instance:
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
            logger.error(f"Erro ao carregar os módulos no manager: {e}", exc_info=True)

    def open_module_tab(self, module_id: str, title: str, content_widget: QtWidgets.QWidget):
        """Adiciona uma nova aba para o módulo e mapeia seu ID."""
        self._widget_to_module_id[content_widget] = module_id
        self.tab_controller.add_tab(title, content_widget)
        self.module_opened.emit(module_id)

    def get_active_module(self) -> Optional[IModule]:
        """Retorna o módulo atualmente ativo."""
        try:
            current_widget = self.tab_controller.container.currentWidget()
            if current_widget and current_widget in self._widget_to_module_id:
                module_id = self._widget_to_module_id[current_widget]
                if hasattr(self.registry, "get_or_create_module"):
                    return self.registry.get_or_create_module(module_id)
        except Exception as e:
            logger.error(f"Erro ao obter módulo ativo no manager: {e}")
        return None

    # =========================================================================
    # EVENT HANDLERS (PRIVATE)
    # =========================================================================
    def _handle_tab_changed(self, index: int):
        """Disparado quando o usuário troca de aba visualmente."""
        try:
            if hasattr(self.tab_controller, "tabs") and 0 <= index < len(self.tab_controller.tabs):
                current_tab = self.tab_controller.tabs[index]
                current_widget = self.tab_controller._tab_to_widget.get(current_tab)

                if current_widget and current_widget in self._widget_to_module_id:
                    module_id = self._widget_to_module_id[current_widget]
                    if hasattr(self, "on_module_changed"):
                        self.on_module_changed(module_id)
                        return

            active_modules = self.registry.list_active_modules()
            if 0 <= index < len(active_modules):
                module_id = active_modules[index]
                if hasattr(self, "on_module_changed"):
                    self.on_module_changed(module_id)
                    return

            current_widget = self.tab_controller.container.currentWidget()
            if current_widget and current_widget in self._widget_to_module_id:
                module_id = self._widget_to_module_id[current_widget]
                if hasattr(self, "on_module_changed"):
                    self.on_module_changed(module_id)

        except Exception as e:
            logger.error(f"Erro ao tratar mudança de aba no index {index}: {e}", exc_info=True)

    def _handle_tab_closed(self, index: int):
        """Disparado quando uma aba é fechada pelo usuário."""
        self.module_closed.emit(index)

        if not self.tab_controller.tabs:
            self._widget_to_module_id.clear()
            from core.workspace.layout.layout import ModuleDistributor
            ModuleDistributor.cleanup(
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )