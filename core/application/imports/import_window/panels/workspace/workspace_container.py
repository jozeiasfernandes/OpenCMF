from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QListView,
)

# Importações dos componentes específicos
from core.application.imports.import_window.panels.workspace.file_browser_view import FileBrowserView
from core.application.imports.import_window.panels.workspace.preview_panel import PreviewPanel


class WorkspaceContainer(QWidget):
    """Painel 3: Container dinâmico responsável por renderizar o workspace conforme a categoria e origem."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget(self)
        self.main_layout.addWidget(self.stack)

        # Tela inicial (placeholder) quando nenhuma seleção completa for feita
        self.placeholder = QLabel("Selecione uma Categoria e uma Origem para continuar", self)
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.placeholder)

        self.current_category = None
        self.current_source = None

        # Dicionário para armazenar instâncias de widgets do workspace já criadas
        self.cached_views = {}

    def update_context(self, category_id: str, source_id: str):
        """Atualiza o contexto e alterna para a visualização correspondente no QStackedWidget."""
        self.current_category = category_id
        self.current_source = source_id

        view_key = f"{category_id}_{source_id}"

        if view_key in self.cached_views:
            self.stack.setCurrentWidget(self.cached_views[view_key])
            return

        target_widget = self._create_view_for_context(category_id, source_id)

        if target_widget:
            self.cached_views[view_key] = target_widget
            self.stack.addWidget(target_widget)
            self.stack.setCurrentWidget(target_widget)
        else:
            self.stack.setCurrentWidget(self.placeholder)

    def _create_view_for_context(self, category_id: str, source_id: str):
        """Fábrica modular para instanciar o layout correto do Painel 3 unindo FileBrowser e PreviewPanel."""

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Vertical)

        # 1. Seção Superior (FileBrowserView ou Lista do Projeto)
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Instancia o PreviewPanel que ficará na parte inferior
        preview_panel = PreviewPanel(self)

        if source_id == "source_file":
            # Instancia o FileBrowserView completo
            file_browser = FileBrowserView(category_id=category_id, parent=self)

            # CONEXÃO CHAVE: Conecta a seleção de arquivo do browser ao painel de preview inferior
            file_browser.file_selected.connect(preview_panel.update_preview)

            top_layout.addWidget(file_browser)
        else:
            # Origem "Do Projeto"
            project_label = QLabel(f"Itens salvos no projeto para [{category_id}]:", self)
            top_layout.addWidget(project_label)
            project_list = QListView(self)
            top_layout.addWidget(project_list)

        splitter.addWidget(top_widget)

        # 2. Seção Inferior (PreviewPanel integrado)
        splitter.addWidget(preview_panel)

        # Proporção de tamanho entre o explorador superior e o preview inferior
        splitter.setSizes([380, 120])
        layout.addWidget(splitter)

        return container