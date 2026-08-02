from pathlib import Path
from PySide6 import QtWidgets
from typing import Dict, Optional

from settings.settings_app_manager import settings
from core.workspace.containers.side_panel_container.side_panel_drawer_mixin import SidePanelDrawerMixin
from core.workspace.containers.side_panel_container.base.base_side_panel_container import BaseSidePanelMode

# Importação dos modos específicos baseados na estratégia
from core.workspace.containers.side_panel_container.tabs_panel_mode.tabs_container import TabsSidePanelMode
from core.workspace.containers.side_panel_container.toolbox_panel_mode.toolbox_container import ToolboxSidePanelMode
from core.workspace.containers.side_panel_container.floating_panel_mode.floating_container import FloatingSidePanelMode

from core.workspace.containers.side_panel_container.tabs_panel_mode.side_panel_header_tabs import SidePanelHeaderTabs
from core.workspace.containers.side_panel_container.toolbox_panel_mode.side_panel_header_toolbox import \
    SidePanelHeaderToolbox
from core.workspace.containers.side_panel_container.floating_panel_mode.side_panel_header_floating import \
    SidePanelHeaderFloating


class SidePanelContainer(QtWidgets.QWidget, SidePanelDrawerMixin):
    """
    Container visual principal que gerencia o ciclo de vida dos painéis laterais
    e delega a exibição para a estratégia correspondente ao modo atual (Tabs, Toolbox ou Floating).
    """

    def __init__(self, title: str = "Side Panel", workspace_manager=None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.workspace_manager = workspace_manager

        # Layout principal horizontal
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.current_mode = settings.side_panel_mode
        self.panels: Dict[str, QtWidgets.QWidget] = {}
        self.panel_titles: Dict[str, str] = {}

        # Instância da estratégia ativa de exibição
        self.mode_strategy: Optional[BaseSidePanelMode] = None

        # Container de conteúdo interno padrão
        self.content_container = QtWidgets.QWidget(self)
        self.content_layout = QtWidgets.QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.header = None

        self._init_layout_mode(title)

    def _init_layout_mode(self, title: str):
        """Inicializa a estratégia do modo ativo sem exibir o cabeçalho redundante superior."""
        # Limpa completamente o layout de conteúdo antes de popular novamente
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            if item and item.widget():
                w = item.widget()
                if w != self.mode_strategy:
                    w.setParent(None)

        self.header = None

        self._setup_strategy()

        if self.current_mode == "floating":
            self.setVisible(False)
            if self.main_layout.indexOf(self.content_container) == -1:
                self.main_layout.addWidget(self.content_container, stretch=1)
        else:
            if self.main_layout.indexOf(self.content_container) == -1:
                self.main_layout.addWidget(self.content_container, stretch=1)

    def _setup_header(self, title: str):
        """Configura e substitui o cabeçalho de forma limpa, evitando sobreposições."""
        if hasattr(self, "header") and self.header:
            self.content_layout.removeWidget(self.header)
            self.header.setParent(None)
            self.header.deleteLater()
            self.header = None

        if self.current_mode == "settings_page_tabs":
            self.header = SidePanelHeaderTabs(title, workspace_manager=self.workspace_manager, parent=self)
            self.header.toggle_collapsed_changed.connect(self.apply_drawer_state)
        elif self.current_mode == "toolbox":
            self.header = SidePanelHeaderToolbox(title, workspace_manager=self.workspace_manager, parent=self)
            self.header.toggle_collapsed_changed.connect(self.apply_drawer_state)
        else:
            self.header = SidePanelHeaderFloating(title, workspace_manager=self.workspace_manager, parent=self)
            if hasattr(self.header, "dock_requested"):
                self.header.dock_requested.connect(self._on_dock_requested)

        self.content_layout.insertWidget(0, self.header)

    def _setup_strategy(self):
        """Instancia a estratégia correspondente utilizando o padrão BaseSidePanelMode."""
        if self.mode_strategy:
            if isinstance(self.mode_strategy, QtWidgets.QWidget):
                self.content_layout.removeWidget(self.mode_strategy)
                self.mode_strategy.setParent(None)
                self.mode_strategy.deleteLater()
            self.mode_strategy = None

        if self.current_mode == "settings_page_tabs":
            self.mode_strategy = TabsSidePanelMode(self.content_container)
            self.content_layout.addWidget(self.mode_strategy)
        elif self.current_mode == "toolbox":
            self.mode_strategy = ToolboxSidePanelMode(self.content_container)
            self.content_layout.addWidget(self.mode_strategy)
        elif self.current_mode == "floating":
            parent_window = self.window() if isinstance(self.window(), QtWidgets.QMainWindow) else None
            self.mode_strategy = FloatingSidePanelMode(container=None, title="Painel Flutuante")
            if hasattr(self.mode_strategy, "dock_requested"):
                self.mode_strategy.dock_requested.connect(self._on_dock_requested)

            if parent_window:
                geom = parent_window.geometry()
                self.mode_strategy.resize(320, 500)
                self.mode_strategy.move(geom.right() - 340, geom.top() + 60)
            self.mode_strategy.show()

    def _on_dock_requested(self):
        """Reanexa o painel flutuante de volta para o workspace alterando para o modo Toolbox."""
        if self.mode_strategy and self.current_mode == "floating":
            self.mode_strategy.close()
            self.mode_strategy = None

        self.current_mode = "toolbox"
        settings.side_panel_mode = "toolbox"
        settings.save()

        self.setVisible(True)
        self._init_layout_mode("Side Panel")

        # Reinsere os painéis existentes na nova estratégia
        for panel_id, panel in self.panels.items():
            title = self.panel_titles.get(panel_id, panel_id.replace("_", " ").title())
            if self.mode_strategy:
                self.mode_strategy.add_panel(panel_id, panel, title)
            panel.setVisible(True)

    def add_panel(self, panel_id: str, panel: QtWidgets.QWidget, title: str = "Panel"):
        """Adiciona um painel delegando a operação para a estratégia ativa."""
        if panel_id in self.panels:
            self.remove_panel(panel_id)

        if title == "Panel":
            title = getattr(panel, "side_panel_name", None) or panel_id.replace("_", " ").title()

        self.panels[panel_id] = panel
        self.panel_titles[panel_id] = title

        if self.mode_strategy:
            self.mode_strategy.add_panel(panel_id, panel, title)

        panel.setVisible(True)

    def remove_panel(self, panel_id: str):
        """Remove o painel da estratégia ativa sem destruí-lo (preservando cache)."""
        if panel := self.panels.pop(panel_id, None):
            self.panel_titles.pop(panel_id, None)

            if self.mode_strategy:
                self.mode_strategy.remove_panel(panel_id)

            panel.setVisible(False)
            panel.setParent(None)

    def remover_widget_por_caminho(self, caminho: Path):
        """Remove um painel com base no caminho do módulo correspondente."""
        for panel_id, panel in list(self.panels.items()):
            mod_path = panel.property("__module_path__")
            if mod_path and Path(mod_path) == Path(caminho):
                self.remove_panel(panel_id)
                break

    def clear_all(self):
        """
        Remove todos os painéis gerenciados SEM destruí-los,
        preservando suas instâncias para reuso (cache).
        """
        for panel_id in list(self.panels.keys()):
            self.remove_panel(panel_id)
        if self.mode_strategy and hasattr(self.mode_strategy, "clear"):
            self.mode_strategy.clear()

    def atualizar_largura(self, width: int):
        """Método de compatibilidade para redimensionamento."""
        if self.current_mode == "floating" and self.mode_strategy and hasattr(self.mode_strategy, "resize"):
            self.mode_strategy.resize(width, self.mode_strategy.height())

    @property
    def floating_window(self):
        """Propriedade de compatibilidade para referenciar a janela flutuante quando em modo floating."""
        return self.mode_strategy if self.current_mode == "floating" else None

    def reattach_panels_to_new_container(self, new_container):
        """Reanexa os painéis em cache para o novo container sem duplicações."""
        for panel_id, panel in list(self.panels.items()):
            title = self.panel_titles.get(panel_id, panel_id.replace("_", " ").title())
            if new_container and hasattr(new_container, "add_panel"):
                new_container.add_panel(panel_id, panel, title)
            if panel:
                panel.setVisible(True)