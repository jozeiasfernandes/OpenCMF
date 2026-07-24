from pathlib import Path
from PySide6 import QtWidgets, QtCore
from typing import Dict, Optional

from core.settings.settings_app_manager import settings

from core.workspace.containers.side_panel_container.collapsible_section import CollapsibleSection
from .side_panel_header import SidePanelHeader


class SidePanelContainer(QtWidgets.QWidget):
    """
    Container visual que alterna dinamicamente entre Abas Laterais (East),
    Toolbox (Painéis Empilhados customizados via CollapsibleSection) ou Painel Flutuante
    com base nas preferências do usuário.
    """

    def __init__(self, title: str = "Side Panel", workspace_manager=None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.workspace_manager = workspace_manager

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Identifica o modo salvo ("tabs", "toolbox" ou "floating")
        self.current_mode = settings.side_panel_mode

        # Se estiver no modo flutuante, o painel lateral fixo fica oculto por padrão
        if self.current_mode == "floating":
            self.setVisible(False)

        self.panels: Dict[str, QtWidgets.QWidget] = {}
        self.panel_titles: Dict[str, str] = {}
        self.collapsible_sections: Dict[str, CollapsibleSection] = {}

        # Cria o cabeçalho fixo no topo
        self._setup_header(title)

        # Cria a área de conteúdo abaixo do cabeçalho
        self._setup_mode_widget()

    def _setup_header(self, title: str):
        """Configura o cabeçalho do painel lateral."""
        self.header = SidePanelHeader(title, workspace_manager=self.workspace_manager, parent=self)
        self.header.toggle_colapsado_alterado.connect(self._on_toggle_colapsado)
        self.main_layout.addWidget(self.header)

    def _setup_mode_widget(self):
        """Configura o widget interno de acordo com o modo escolhido."""
        self.content_container = QtWidgets.QWidget(self)
        content_layout = QtWidgets.QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        if self.current_mode == "tabs":
            # Modo Abas Laterais (QTabWidget com abas na vertical à direita - East)
            self.content_widget = QtWidgets.QTabWidget()
            self.content_widget.setTabPosition(QtWidgets.QTabWidget.East)
            self.content_widget.setDocumentMode(True)
            content_layout.addWidget(self.content_widget)
        else:
            # Modo Toolbox ou Floating (utiliza estrutura de painéis empilhados/colapsáveis)
            self.scroll_area = QtWidgets.QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

            self.toolbox_container = QtWidgets.QWidget()
            self.toolbox_layout = QtWidgets.QVBoxLayout(self.toolbox_container)
            self.toolbox_layout.setContentsMargins(0, 0, 0, 0)
            self.toolbox_layout.setSpacing(4)
            self.toolbox_layout.addStretch()  # Mantém os painéis empilhados no topo

            self.scroll_area.setWidget(self.toolbox_container)
            content_layout.addWidget(self.scroll_area)

        self.main_layout.addWidget(self.content_container)

    def _on_toggle_colapsado(self, colapsado: bool):
        """Oculta ou exibe a área de conteúdo mantendo o cabeçalho visível."""
        self.content_container.setVisible(not colapsado)

    def add_panel(self, panel_id: str, panel: QtWidgets.QWidget, title: str = "Panel"):
        """Adiciona um painel como aba ou como seção do toolbox com o CollapsibleSection."""
        if panel_id in self.panels:
            self.remove_panel(panel_id)

        if title == "Panel":
            title = getattr(panel, "side_panel_name", None) or panel_id.replace("_", " ").title()

        self.panels[panel_id] = panel
        self.panel_titles[panel_id] = title

        if self.current_mode == "tabs":
            self.content_widget.addTab(panel, title)
        else:
            section = CollapsibleSection(title, panel)
            self.collapsible_sections[panel_id] = section
            self.toolbox_layout.insertWidget(self.toolbox_layout.count() - 1, section)

        panel.setVisible(True)

    def remove_panel(self, panel_id: str):
        """Remove o painel do container ativo."""
        if panel := self.panels.pop(panel_id, None):
            self.panel_titles.pop(panel_id, None)
            if hasattr(panel, 'dispose') and callable(panel.dispose):
                panel.dispose()

            if self.current_mode == "tabs":
                idx = self.content_widget.indexOf(panel)
                if idx != -1:
                    self.content_widget.removeTab(idx)
            else:
                if section := self.collapsible_sections.pop(panel_id, None):
                    self.toolbox_layout.removeWidget(section)
                    section.setParent(None)
                    section.deleteLater()

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

    def atualizar_largura(self, width: int):
        """Método mantido por compatibilidade; o redimensionamento dinâmico agora é gerido pelo QSplitter via mouse."""
        pass