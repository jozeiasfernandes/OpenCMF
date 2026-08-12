from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTreeWidgetItem, QTreeWidget, QVBoxLayout, QWidget

# Settings
from core.settings.icons_manager.icon_manager import IconManager
from core.settings.localization.translator import tr


class SourcePanel(QWidget):
  """Painel 2: Árvore de origem de importação (Local: Do projeto / Do arquivo)."""

  source_selected = Signal(str)

  def __init__(self, parent=None):
    super().__init__(parent)
    layout = QVBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)

    self.tree = QTreeWidget()
    self.tree.setHeaderHidden(True)
    self.tree.setRootIsDecorated(False)

    icon_mgr = IconManager.get_instance()
    self.arrow_right_icon = icon_mgr.get_icon("arrow_right", size=16)
    self.arrow_down_icon = icon_mgr.get_icon("arrow_down", size=16)

    self.sources_structure = [
        {
            "key": "import.sources.project_manager.name",
            "id": "source_project",
            "children": [],
        },
        {"key": "import.sources.file.name", "id": "source_file", "children": []},
    ]

    # Item raiz estático representando "LOCAL:"
    self.root_item = QTreeWidgetItem(self.tree)
    self.root_item.setText(0, "LOCAL:")
    self.root_item.setFlags(
        self.root_item.flags() & ~Qt.ItemIsSelectable
    )  # Não selecionável

    for src in self.sources_structure:
      item = QTreeWidgetItem(self.root_item)
      text = tr(src["key"])
      capitalized_text = text[:1].upper() + text[1:] if text else text
      item.setText(0, capitalized_text)
      item.setData(0, 32, src["id"])

    self.tree.expandAll()
    self.tree.itemClicked.connect(self._on_item_clicked)
    layout.addWidget(self.tree)

  def load_sources_for_category(self, category_id: str):
    """Método chamado pelo ImportWindow para atualizar/contextualizar

    as origens com base na categoria selecionada no Painel 1, se necessário.
    """
    self.current_category_id = category_id
    # Mantém a estrutura padrão de fontes visível e expandida
    self.tree.expandAll()

  def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
    # Ignora o clique caso seja o item raiz "LOCAL:"
    if item == self.root_item:
      return

    source_id = item.data(0, 32)
    if source_id:
      self.source_selected.emit(source_id)


if __name__ == "__main__":
  import sys
  from PySide6.QtWidgets import QApplication

  app = QApplication(sys.argv)

  panel = SourcePanel()
  panel.resize(250, 400)
  panel.show()

  panel.source_selected.connect(
      lambda source_id: print(f"Origem selecionada: {source_id}")
  )

  sys.exit(app.exec())