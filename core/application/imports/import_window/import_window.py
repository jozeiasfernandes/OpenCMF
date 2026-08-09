from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QWidget

# Panels
from core.application.imports.import_window.panels.category_panel import (
    CategoryPanel,
)
from core.application.imports.import_window.panels.source_panel import SourcePanel
from core.application.imports.import_window.panels.workspace.workspace_container import (
    WorkspaceContainer,
)


class ImportWindow(QMainWindow):
  """Janela principal de importação integrando os três painéis lado a lado."""

  def __init__(self):
    super().__init__()
    self.setWindowTitle("Gerenciador de Importações")
    self.resize(1200, 600)

    # Widget Central e Layout principal
    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    main_layout = QHBoxLayout(central_widget)
    main_layout.setContentsMargins(2, 2, 2, 2)

    # Splitter principal horizontal para os 3 painéis
    splitter = QSplitter(Qt.Horizontal)

    # Instanciando os três painéis
    self.category_panel = CategoryPanel()  # Painel 1 (Categorias)
    self.source_panel = SourcePanel()  # Painel 2 (Origem / Local)
    self.workspace_container = (
        WorkspaceContainer()
    )  # Painel 3 (Workspace / Conteúdo)

    # O Painel 2 começa desativado/vazio até que o Painel 1 tenha uma seleção de subcategoria válida
    self.source_panel.setEnabled(False)

    # Adicionando os três diretamente ao splitter na horizontal (o Painel 3 sempre aparece)
    splitter.addWidget(self.category_panel)
    splitter.addWidget(self.source_panel)
    splitter.addWidget(self.workspace_container)

    # Definindo tamanhos iniciais em pixels para forçar a renderização dos 3 painéis visíveis
    splitter.setSizes([250, 250, 700])

    # Definindo proporções de redimensionamento dinâmico
    splitter.setStretchFactor(0, 1)  # Painel 1
    splitter.setStretchFactor(1, 1)  # Painel 2
    splitter.setStretchFactor(2, 3)  # Painel 3

    main_layout.addWidget(splitter)

    # Conexão de Sinais
    self.category_panel.category_selected.connect(
        self._handle_category_selection
    )
    self.source_panel.source_selected.connect(self._handle_selection_change)

  def _handle_category_selection(self, category_id=None):
    """Gerencia a seleção do Painel 1: verifica se é subcategoria e gerencia o Painel 2."""
    current_cat = self.category_panel.tree.currentItem()
    cat_id = current_cat.data(0, 32) if current_cat else category_id

    # Condicional: se o item selecionado for uma categoria principal (pai),
    # ela serve apenas para expandir/ocultar e não deve habilitar o Painel 2.
    # O Painel 2 só é habilitado se for uma subcategoria (item filho).
    is_subCategory = current_cat and current_cat.parent() is not None

    if is_subCategory and cat_id:
      self.source_panel.setEnabled(True)
      if hasattr(self.source_panel, "load_sources_for_category"):
        self.source_panel.load_sources_for_category(cat_id)
    else:
      self.source_panel.setEnabled(False)
      # Limpa a seleção do painel 2 se voltar a clicar em uma categoria pai
      self.source_panel.tree.clearSelection()

    self._handle_selection_change()

  def _handle_selection_change(self, source_id=None):
    """Atualiza o WorkspaceContainer com base nas condicionais de categoria e origem."""
    current_cat = self.category_panel.tree.currentItem()
    current_src = self.source_panel.tree.currentItem()

    cat_id = current_cat.data(0, 32) if current_cat else None
    src_id = current_src.data(0, 32) if current_src else source_id

    # O Painel 3 só carrega o contexto dinâmico se houver subcategoria e origem válidas
    if cat_id and src_id and current_cat and current_cat.parent() is not None:
      self.workspace_container.update_context(cat_id, src_id)


if __name__ == "__main__":
  import sys
  from PySide6.QtWidgets import QApplication

  app = QApplication(sys.argv)
  window = ImportWindow()
  window.show()
  sys.exit(app.exec())