from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSplitter,
    QListView,
    QPushButton,
)

# Importações dos componentes específicos
from core.application.file_browser.file_browser_view import FileBrowserView
from core.application.imports.import_window.panels.workspace.preview_panel import PreviewPanel


class WorkspaceContainer(QWidget):
    """Painel 3: Container dinâmico responsável por renderizar o workspace conforme a categoria e origem."""

    # Sinal emitido quando o usuário clica em importar com um arquivo válido
    import_requested = Signal(str)

    # Mapeamento de filtros de extensão por ID de categoria
    CATEGORY_FILTERS = {
        "volume": ["*.dcm", "*.vti", "*.vtk", "*.nrrd", "*.nii", "*.nii.gz", "*.mhd", "*.mha"],
        "dicom": ["*.dcm", "DICOMDIR"],
        "photo": ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif", "*.tiff"],
        "mesh": ["*.stl", "*.obj", "*.ply", "*.off", "*.vtp", "*.vtk"],
        "implant": ["*.stl", "*.obj", "*.ply", "*.step", "*.stp", "*.iges", "*.igs"],
        "scan": ["*.stl", "*.obj", "*.ply", "*.vtp"],
    }

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
        """Fábrica modular para instanciar o layout correto do Painel 3 unindo FileBrowser, PreviewPanel e Botão Importar."""

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

        # Referência para armazenar o browser ativo no escopo da função
        file_browser = None

        if source_id == "source_file":
            category_lower = category_id.strip().lower()
            filters = []
            for key, ext_list in self.CATEGORY_FILTERS.items():
                if key in category_lower:
                    filters = ext_list
                    break

            file_browser = FileBrowserView(name_filters=filters, parent=self)
            file_browser.file_selected.connect(preview_panel.update_preview)

            top_layout.addWidget(file_browser)
        else:
            project_label = QLabel(f"Itens salvos no projeto para [{category_id}]:", self)
            top_layout.addWidget(project_label)
            project_list = QListView(self)
            top_layout.addWidget(project_list)

        # Barra de Ações Inferior contendo o Botão Importar
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 5, 0, 0)

        btn_import = QPushButton("Importar", self)
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        # Estilização opcional para destacar o botão principal de ação
        btn_import.setStyleSheet("font-weight: bold; padding: 6px 16px;")

        # Conexão do botão de importação
        def on_import_clicked():
            if file_browser:
                selected_path = file_browser.selected_file()
                if selected_path:
                    self.import_requested.emit(selected_path)
                    print(f"[Importação Acionada]: {selected_path}")

        btn_import.clicked.connect(on_import_clicked)

        action_layout.addStretch()
        action_layout.addWidget(btn_import)
        top_layout.addLayout(action_layout)

        splitter.addWidget(top_widget)

        # 2. Seção Inferior (PreviewPanel integrado)
        splitter.addWidget(preview_panel)

        splitter.setSizes([380, 120])
        layout.addWidget(splitter)

        return container