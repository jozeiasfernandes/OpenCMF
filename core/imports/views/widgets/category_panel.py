from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from core.imports.models.import_category import ImportCategory
from core.settings.localization.translator import tr


class CategoryPanel(QWidget):
    """Panel responsible for displaying and managing import categories."""

    category_changed = Signal(ImportCategory)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Title
        layout.addWidget(QLabel(tr("import.panels.categories", "Categorias")))

        # List widget for categories
        self.list = QListWidget()

        for category in ImportCategory:
            item = QListWidgetItem(category.display_name)
            item.setData(Qt.UserRole, category)
            self.list.addItem(item)

        self.list.currentRowChanged.connect(self._on_changed)
        layout.addWidget(self.list)

        # Select the first item by default if available
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def _on_changed(self, row: int) -> None:
        item = self.list.item(row)
        if item:
            category: ImportCategory = item.data(Qt.UserRole)
            self.category_changed.emit(category)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = CategoryPanel()
    panel.resize(300, 400)
    panel.show()
    sys.exit(app.exec())