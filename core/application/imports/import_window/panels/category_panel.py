from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTreeWidgetItem, QTreeWidget, QVBoxLayout, QWidget

# Settings
from core.settings.icons.icon_manager import IconManager
from core.settings.localization.translator import tr

class CategoryPanel(QWidget):
  """Painel 1: Árvore de categorias de importação com expansão estilo PyCharm."""

  category_selected = Signal(str)

  def __init__(self, parent=None):
    super().__init__(parent)
    layout = QVBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)

    self.tree = QTreeWidget()
    self.tree.setHeaderHidden(True)
    # Desativa a indicação padrão do Qt para usarmos apenas o ícone customizado
    self.tree.setRootIsDecorated(False)

    icon_mgr = IconManager.get_instance()
    self.arrow_right_icon = icon_mgr.get_icon("arrow_right", size=16)
    self.arrow_down_icon = icon_mgr.get_icon("arrow_down", size=16)

    self.categories_structure = [
        {
            "key": "import.categories.volume",
            "id": "volume",
            "children": [
                {"key": "import.volumes.dicom", "id": "volume_dicom"},
                {"key": "import.volumes.vti", "id": "volume_vti"},
                {"key": "import.volumes.vtk_nrrd_nifti", "id": "volume_other"},
            ],
        },
        {
            "key": "import.categories.radiography",
            "id": "radiography",
            "children": [
                {"key": "import.radiographies.panoramic", "id": "rad_panoramic"},
                {
                    "key": "import.radiographies.teleradiography",
                    "id": "rad_teleradiography",
                },
                {"key": "import.radiographies.intrabuccal", "id": "rad_intrabuccal"},
                {
                    "key": "import.radiographies.reconstructed_panoramic",
                    "id": "rad_reconst_panoramic",
                },
                {
                    "key": "import.radiographies.reconstructed_teleradiography",
                    "id": "rad_reconst_telerad",
                },
            ],
        },
        {
            "key": "import.categories.scan",
            "id": "scan",
            "children": [
                {"key": "import.scans.face", "id": "scan_face"},
                {"key": "import.scans.dental_arches", "id": "scan_arches"},
                {
                    "key": "import.scans.photogrammetry",
                    "id": "scan_photogrammetry",
                },
            ],
        },
        {
            "key": "import.categories.photo",
            "id": "photo",
            "children": [
                {"key": "import.photographs.front", "id": "photo_front"},
                {"key": "import.photographs.profile", "id": "photo_profile"},
                {
                    "key": "import.photographs.intrabuccal",
                    "id": "photo_intrabuccal",
                },
                {"key": "import.photographs.others", "id": "photo_others"},
            ],
        },
        {
            "key": "import.categories.mesh",
            "id": "mesh",
            "children": [
                {"key": "import.mesh_items.objects_3d", "id": "mesh_3d"},
                {
                    "key": "import.mesh_items.objects_3d_online",
                    "id": "mesh_online",
                },
            ],
        },
        {
            "key": "import.categories.dental_implant",
            "id": "dental_implant",
            "children": [
                {
                    "key": "import.dental_implant_items.dental_implants",
                    "id": "dental_implants_list",
                },
                {
                    "key": "import.dental_implant_items.resources",
                    "id": "dental_resources",
                },
            ],
        },
        {
            "key": "import.categories.facial_implant",
            "id": "facial_implant",
            "children": [
                {
                    "key": "import.facial_implant_items.mandibular_angle",
                    "id": "facial_angle",
                },
                {
                    "key": "import.facial_implant_items.zygomatic",
                    "id": "facial_zygomatic",
                },
                {
                    "key": "import.facial_implant_items.paranasal",
                    "id": "facial_paranasal",
                },
                {"key": "import.facial_implant_items.mento", "id": "facial_mento"},
            ],
        },
    ]

    for cat in self.categories_structure:
      parent_item = QTreeWidgetItem(self.tree)
      # Categoria em MAIÚSCULA
      parent_item.setText(0, tr(cat["key"]).upper())
      parent_item.setData(0, 32, cat["id"])

      if cat.get("children"):
        # Define ícone inicial para expandido (seta para baixo)
        parent_item.setIcon(0, self.arrow_down_icon)

      for child in cat.get("children", []):
        child_item = QTreeWidgetItem(parent_item)
        # Subcategoria com a primeira letra em maiúscula
        text = tr(child["key"])
        capitalized_text = text[:1].upper() + text[1:] if text else text
        child_item.setText(0, capitalized_text)
        child_item.setData(0, 32, child["id"])

      # Garante que por padrão a lista inicia expandida
      parent_item.setExpanded(True)

    self.tree.itemClicked.connect(self._on_item_clicked)
    self.tree.itemExpanded.connect(self._on_item_expanded)
    self.tree.itemCollapsed.connect(self._on_item_collapsed)

    layout.addWidget(self.tree)

  def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
    # Se for uma categoria principal (pai), apenas alterna a expansão e não emite seleção válida para o fluxo de importação
    if item.childCount() > 0:
      item.setExpanded(not item.isExpanded())
    else:
      # Se for uma subcategoria (filha), emite o ID correspondente
      cat_id = item.data(0, 32)
      if cat_id:
        self.category_selected.emit(cat_id)

  def _on_item_expanded(self, item: QTreeWidgetItem):
    if item.childCount() > 0:
      item.setIcon(0, self.arrow_down_icon)

  def _on_item_collapsed(self, item: QTreeWidgetItem):
    if item.childCount() > 0:
      item.setIcon(0, self.arrow_right_icon)


if __name__ == "__main__":
  import sys
  from PySide6.QtWidgets import QApplication

  app = QApplication(sys.argv)

  panel = CategoryPanel()
  panel.resize(320, 500)
  panel.show()

  panel.category_selected.connect(
      lambda cat_id: print(f"Subcategoria selecionada: {cat_id}")
  )

  sys.exit(app.exec())