from pathlib import Path
from PySide6 import QtWidgets, QtCore
from typing import Dict, Optional
from core.settings.settings_app_manager import settings
from .collapsible_section import CollapsibleSection


class SidePanelContainer(QtWidgets.QWidget):
    """
    Container visual que alterna dinamicamente entre Abas Laterais (East)
    e Toolbox (Painéis Empilhados customizados via CollapsibleSection) com base nas preferências do usuário.
    """

    def __init__(self, title: str = "Side Panel", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Aplica a largura inicial configurada nas preferências
        initial_width = settings.side_panel_width
        self.setFixedWidth(initial_width)

        self.panels: Dict[str, QtWidgets.QWidget] = {}
        self.panel_titles: Dict[str, str] = {}
        self.collapsible_sections: Dict[str, CollapsibleSection] = {}

        # Identifica o modo salvo ("tabs" ou "toolbox")
        self.current_mode = settings.side_panel_mode

        self._setup_mode_widget()

    def _setup_mode_widget(self):
        """Configura o widget interno de acordo com o modo escolhido."""
        if self.current_mode == "tabs":
            # Modo Abas Laterais (QTabWidget com abas na vertical à direita - East)
            self.content_widget = QtWidgets.QTabWidget()
            self.content_widget.setTabPosition(QtWidgets.QTabWidget.East)
            self.content_widget.setDocumentMode(True)
            self.main_layout.addWidget(self.content_widget)
        else:
            # Modo Toolbox customizado com rolagem para suportar os painéis empilhados colapsáveis
            self.scroll_area = QtWidgets.QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

            self.toolbox_container = QtWidgets.QWidget()
            self.toolbox_layout = QtWidgets.QVBoxLayout(self.toolbox_container)
            self.toolbox_layout.setContentsMargins(0, 0, 0, 0)
            self.toolbox_layout.setSpacing(4)
            self.toolbox_layout.addStretch()  # Mantém os painéis empilhados no topo

            self.scroll_area.setWidget(self.toolbox_container)
            self.main_layout.addWidget(self.scroll_area)

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
            # Insere antes do stretch (último item do layout)
            self.toolbox_layout.insertWidget(self.toolbox_layout.count() - 1, section)

        panel.setVisible(True)

    def remove_panel(self, panel_id: str):
        """Remove o painel do container ativo."""
        if panel := self.panels.pop(panel_id, None):
            self.panel_titles.pop(panel_id, None)
            if hasattr(panel, 'dispose') and callable(panel.dispose):
                panel.dispose()

            # Remove do widget correspondente
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
        """Atualiza a largura do painel lateral ajustando o QSplitter pai."""
        self.setMaximumWidth(16777215)
        self.setMinimumWidth(150)

        splitter = self.parent()
        while splitter and not isinstance(splitter, QtWidgets.QSplitter):
            splitter = splitter.parent()

        if splitter:
            sizes = splitter.sizes()
            total_width = sum(sizes)
            if total_width > 0:
                central_width = total_width - width
                splitter.setSizes([central_width, width])
        else:
            self.setFixedWidth(width)