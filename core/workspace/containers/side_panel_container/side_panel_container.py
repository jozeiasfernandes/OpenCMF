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

        # Layout principal horizontal: [Conteúdo (Cabeçalho + Widgets)] + [QTabWidget Fixo à Direita (East)]
        self.main_layout = QtWidgets.QHBoxLayout(self)
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

        # 1. Container de conteúdo ocultável (Cabeçalho + Área de Ferramentas)
        self.content_container = QtWidgets.QWidget(self)
        self.content_layout = QtWidgets.QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Cria o cabeçalho fixo no topo do content_container
        self._setup_header(title)

        # Cria a área de conteúdo abaixo do cabeçalho
        self._setup_mode_widget()

        self.main_layout.addWidget(self.content_container, stretch=1)

        # 2. QTabWidget lateral fixo (TabPosition East) - Fica fora da área que é ocultada
        # Renderiza as abas verticais permanentemente na faixa lateral compacta
        self.vertical_tabs = QtWidgets.QTabWidget(self)
        self.vertical_tabs.setTabPosition(QtWidgets.QTabWidget.East)
        self.vertical_tabs.setObjectName("SidePanelVerticalTabs")
        self.vertical_tabs.setFixedWidth(35)

        # Conecta o sinal após a criação correta de self.vertical_tabs
        self.vertical_tabs.currentChanged.connect(self._on_vertical_tab_clicked)

        # Se não estiver no modo tabs, ocultamos este tabwidget auxiliar para não ocupar espaço indevido
        if self.current_mode == "tabs":
            self.main_layout.addWidget(self.vertical_tabs)
        else:
            self.vertical_tabs.setVisible(False)

    def _setup_header(self, title: str):
        """Configura o cabeçalho do painel lateral."""
        self.header = SidePanelHeader(title, workspace_manager=self.workspace_manager, parent=self)
        self.header.toggle_colapsado_alterado.connect(self._on_toggle_colapsado)
        self.content_layout.addWidget(self.header)

    def _setup_mode_widget(self):
        """Configura o widget interno de acordo com o modo escolhido."""
        if self.current_mode == "tabs":
            # Modo Abas Laterais (QTabWidget interno principal)
            self.content_widget = QtWidgets.QTabWidget()
            self.content_widget.setTabPosition(QtWidgets.QTabWidget.East)
            self.content_widget.setDocumentMode(True)
            self.content_layout.addWidget(self.content_widget)
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
            self.content_layout.addWidget(self.scroll_area)

    def _on_toggle_colapsado(self, colapsado: bool):
        """Oculta apenas o conteúdo interno e redimensiona o QSplitter para deixar a faixa lateral visível."""
        self.content_container.setVisible(not colapsado)

        # Encontra o splitter pai para ajustar dinamicamente o tamanho do painel
        splitter = self.parent()
        while splitter and not isinstance(splitter, QtWidgets.QSplitter):
            splitter = splitter.parent()

        if colapsado:
            # Fixa uma largura menor suficiente apenas para exibir a barra compacta
            self.setMaximumWidth(45)
            self.setMinimumWidth(35)
            if splitter:
                sizes = splitter.sizes()
                total = sum(sizes)
                if total > 0:
                    # Deixa quase todo o espaço para a área central e 40px para o side panel
                    splitter.setSizes([total - 40, 40])
        else:
            # Libera o painel para voltar ao tamanho normal gerido pelo usuário
            self.setMaximumWidth(16777215)  # QWIDGETSIZE_MAX do Qt
            self.setMinimumWidth(100)
            if splitter:
                sizes = splitter.sizes()
                total = sum(sizes)
                if total > 0:
                    # Restaura proporção padrão de 70% / 30%
                    central_w = int(total * 0.70)
                    splitter.setSizes([central_w, total - central_w])

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
            # Adiciona também uma aba representativa no container vertical externo fixo para o modo recolhido
            self.vertical_tabs.addTab(QtWidgets.QWidget(), title)
        else:
            section = CollapsibleSection(title, panel)
            self.collapsible_sections[panel_id] = section
            self.toolbox_layout.insertWidget(self.toolbox_layout.count() - 1, section)

        panel.setVisible(True)

    def remove_panel(self, panel_id: str):
        """Remove o painel do container ativo."""
        if panel := self.panels.pop(panel_id, None):
            title = self.panel_titles.pop(panel_id, None)
            if hasattr(panel, 'dispose') and callable(panel.dispose):
                panel.dispose()

            if self.current_mode == "tabs":
                idx = self.content_widget.indexOf(panel)
                if idx != -1:
                    self.content_widget.removeTab(idx)
                # Remove também do tabwidget vertical externo
                for i in range(self.vertical_tabs.count()):
                    if self.vertical_tabs.tabText(i) == title:
                        self.vertical_tabs.removeTab(i)
                        break
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
        """Método mantido por compatibilidade."""
        pass

    def _on_vertical_tab_clicked(self, index: int):
        """Quando o usuário clica em uma aba vertical na faixa compacta, expande o painel e foca na aba."""
        if index < 0:
            return

        # Sincroniza a aba correspondente no widget de conteúdo interno se estiver no modo 'tabs'
        if self.current_mode == "tabs" and hasattr(self, "content_widget"):
            self.content_widget.setCurrentIndex(index)

        # Se o painel estiver colapsado, força a expansão para 70% / 30%
        if hasattr(self, "header") and getattr(self.header, "_colapsado", True):
            # Altera o estado do cabeçalho para expandido
            self.header._colapsado = False
            self.header._update_toggle_icon(False)

            # Restaura a visibilidade dos elementos do cabeçalho
            self.header.lbl_titulo.show()
            self.header.btn_config.show()

            # Mostra o container de conteúdo
            self.content_container.setVisible(True)

            # Restaura a largura máxima/mínima padrão
            self.setMaximumWidth(16777215)
            self.setMinimumWidth(100)

            # Redimensiona o QSplitter pai
            splitter = self.parent()
            while splitter and not isinstance(splitter, QtWidgets.QSplitter):
                splitter = splitter.parent()

            if splitter:
                sizes = splitter.sizes()
                total = sum(sizes)
                if total > 0:
                    central_w = int(total * 0.70)
                    splitter.setSizes([central_w, total - central_w])
                    splitter.update()
                    splitter.repaint()