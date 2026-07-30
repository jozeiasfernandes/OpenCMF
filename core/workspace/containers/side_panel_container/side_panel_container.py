from pathlib import Path
from PySide6 import QtWidgets, QtCore
from typing import Dict, Optional

from core.settings.settings_app_manager import settings

from core.workspace.containers.side_panel_container.side_panel_drawer_mixin import SidePanelDrawerMixin
from core.workspace.containers.side_panel_container.tabs_panel_mode.side_panel_header_tabs import SidePanelHeaderTabs
from core.workspace.containers.side_panel_container.tabs_panel_mode.tabs_container import TabsContainer
from core.workspace.containers.side_panel_container.tabs_panel_mode.collapsible_section_tabs import \
    CollapsibleSectionTabs

from core.workspace.containers.side_panel_container.toolbox_panel_mode.side_panel_header_toolbox import SidePanelHeaderToolbox
from core.workspace.containers.side_panel_container.toolbox_panel_mode.toolbox_container import ToolboxContainer
from core.workspace.containers.side_panel_container.toolbox_panel_mode.collapsible_section_toolbox import \
    CollapsibleSectionToolbox

from core.workspace.containers.side_panel_container.floating_panel_mode.side_panel_header_floating import \
    SidePanelHeaderFloating
from core.workspace.containers.side_panel_container.floating_panel_mode.floating_container import FloatingContainer


class SidePanelContainer(QtWidgets.QWidget, SidePanelDrawerMixin):
    """
    Container visual que alterna dinamicamente entre Abas Laterais (East),
    Toolbox (Painéis Empilhados customizados) ou Painel Flutuante
    com base nas preferências do usuário.
    """

    def __init__(self, title: str = "Side Panel", workspace_manager=None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.workspace_manager = workspace_manager

        # Layout principal horizontal
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Identifica o modo salvo ("tabs", "toolbox" ou "floating")
        self.current_mode = settings.side_panel_mode

        self.panels: Dict[str, QtWidgets.QWidget] = {}
        self.panel_titles: Dict[str, str] = {}
        self.collapsible_sections: Dict[str, QtWidgets.QWidget] = {}

        # Instância da janela flutuante caso o modo seja "floating"
        self.floating_window: Optional[FloatingContainer] = None

        if self.current_mode == "floating":
            self.setVisible(False)
            self._setup_floating_window(title)
        else:
            # 1. Container de conteúdo (Cabeçalho + Área de Ferramentas)
            self.content_container = QtWidgets.QWidget(self)
            self.content_layout = QtWidgets.QVBoxLayout(self.content_container)
            self.content_layout.setContentsMargins(0, 0, 0, 0)
            self.content_layout.setSpacing(0)

            self._setup_header(title)
            self._setup_mode_widget()

            self.main_layout.addWidget(self.content_container, stretch=1)

            # 2. QTabWidget lateral fixo (TabPosition East) apenas para o modo "tabs"
            self.vertical_tabs = QtWidgets.QTabWidget(self)
            self.vertical_tabs.setTabPosition(QtWidgets.QTabWidget.East)
            self.vertical_tabs.setObjectName("SidePanelVerticalTabs")
            self.vertical_tabs.setFixedWidth(35)
            self.vertical_tabs.currentChanged.connect(self._on_vertical_tab_clicked)

            if self.current_mode == "tabs":
                self.main_layout.addWidget(self.vertical_tabs)
            else:
                self.vertical_tabs.setVisible(False)

    def _setup_floating_window(self, title: str):
        """Configura a janela flutuante isolada para o modo floating."""
        if not self.floating_window:
            parent_window = self.window() if isinstance(self.window(), QtWidgets.QMainWindow) else None
            self.floating_window = FloatingContainer(parent=parent_window, title=title)
            self.floating_window.dock_requested.connect(self._on_dock_requested)

            # Posiciona inicialmente no canto superior direito da janela principal
            if parent_window:
                geom = parent_window.geometry()
                self.floating_window.resize(320, 500)
                self.floating_window.move(geom.right() - 340, geom.top() + 60)

            self.floating_window.show()

    def _on_dock_requested(self):
        """Reanexa o painel flutuante de volta para o workspace (Modo Toolbox)."""
        if self.floating_window:
            self.floating_window.close()
            self.floating_window = None
        self.current_mode = "toolbox"
        self.setVisible(True)
        # Recria a interface para o modo Toolbox
        self._setup_header("Side Panel")
        self._setup_mode_widget()

    def _setup_header(self, title: str):
        """Configura o cabeçalho específico de acordo com o modo ativo."""
        if self.current_mode == "tabs":
            self.header = SidePanelHeaderTabs(title, workspace_manager=self.workspace_manager, parent=self)
            self.header.toggle_collapsed_changed.connect(self.apply_drawer_state)
        elif self.current_mode == "toolbox":
            self.header = SidePanelHeaderToolbox(title, workspace_manager=self.workspace_manager, parent=self)
            self.header.toggle_collapsed_changed.connect(self.apply_drawer_state)
        else:
            self.header = SidePanelHeaderFloating(title, workspace_manager=self.workspace_manager, parent=self)
            self.header.dock_requested.connect(self._on_dock_requested)

        self.content_layout.addWidget(self.header)

    def _setup_mode_widget(self):
        """Configura o widget interno adequado (TabsContainer ou ToolboxContainer)."""
        if self.current_mode == "tabs":
            self.content_widget = TabsContainer(self)
            self.content_layout.addWidget(self.content_widget)
        elif self.current_mode == "toolbox":
            self.toolbox_container = ToolboxContainer(self)
            self.content_layout.addWidget(self.toolbox_container)

    def add_panel(self, panel_id: str, panel: QtWidgets.QWidget, title: str = "Panel"):
        """Adiciona um painel como aba, seção do toolbox ou painel flutuante."""
        if panel_id in self.panels:
            self.remove_panel(panel_id)

        if title == "Panel":
            title = getattr(panel, "side_panel_name", None) or panel_id.replace("_", " ").title()

        self.panels[panel_id] = panel
        self.panel_titles[panel_id] = title

        if self.current_mode == "tabs":
            self.content_widget.add_workspace_tab(panel_id, panel, title)
            self.vertical_tabs.addTab(QtWidgets.QWidget(), title)
        elif self.current_mode == "toolbox":
            section = self.toolbox_container.add_section_by_title(title, panel)
            self.collapsible_sections[panel_id] = section
        elif self.current_mode == "floating":
            if not self.floating_window:
                self._setup_floating_window("Painel Flutuante")
            section = self.floating_window.add_section_by_title(title, panel)
            self.collapsible_sections[panel_id] = section

        panel.setVisible(True)

    def remove_panel(self, panel_id: str):
        """Remove o painel do container ativo."""
        if panel := self.panels.pop(panel_id, None):
            title = self.panel_titles.pop(panel_id, None)
            if hasattr(panel, 'dispose') and callable(panel.dispose):
                panel.dispose()

            if self.current_mode == "tabs":
                self.content_widget.remove_workspace_tab(panel_id)
                for i in range(self.vertical_tabs.count()):
                    if self.vertical_tabs.tabText(i) == title:
                        self.vertical_tabs.removeTab(i)
                        break
            elif self.current_mode == "toolbox":
                if section := self.collapsible_sections.pop(panel_id, None):
                    self.toolbox_container.remove_section(section)
            elif self.current_mode == "floating":
                section = self.collapsible_sections.pop(panel_id, None)
                if section and self.floating_window:
                    self.floating_window.remove_section(section)

            panel.setParent(None)
            panel.deleteLater()

    def remover_widget_por_caminho(self, caminho: Path):
        """Remove um painel baseado na propriedade de caminho do módulo."""
        for panel_id, panel in list(self.panels.items()):
            mod_path = panel.property("__module_path__")
            if mod_path and Path(mod_path) == Path(caminho):
                self.remove_panel(panel_id)
                break

    def clear_all(self):
        """Remove todos os painéis."""
        for panel_id in list(self.panels.keys()):
            self.remove_panel(panel_id)
        if self.floating_window:
            self.floating_window.clear_sections()

    def atualizar_largura(self, width: int):
        """Método mantido por compatibilidade."""
        pass

    def _on_vertical_tab_clicked(self, index: int):
        """Quando o usuário clica em uma aba vertical na faixa compacta, expande o painel e foca na aba."""
        if index < 0:
            return

        if self.current_mode == "tabs" and hasattr(self, "content_widget"):
            widget_at_idx = self.content_widget.widget(index)
            if widget_at_idx:
                self.content_widget.setCurrentWidget(widget_at_idx)

        if hasattr(self, "header") and hasattr(self.header, "_collapsed") and self.header._collapsed:
            self.header._collapsed = False
            self.header._update_toggle_icon(False)
            self.header.lbl_title.show()
            self.header.btn_config.show()
            self.apply_drawer_state(False)