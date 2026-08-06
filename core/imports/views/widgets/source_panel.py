from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from core.imports.models.import_category import ImportCategory
from core.imports.models.import_source import ImportSource
from core.settings.localization.translator import tr


class SourcePanel(QWidget):
    """Panel responsible for displaying and managing import sources."""

    source_changed = Signal(ImportSource)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_category: Optional[ImportCategory] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(QLabel(tr("import.panels.source", "Origem")))

        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_changed)
        layout.addWidget(self.list)

        # Populate initially with all available sources
        self._populate_sources()

    def _populate_sources(self, category: Optional[ImportCategory] = None) -> None:
        self.list.clear()
        self._current_category = category

        for source in ImportSource:
            # Filter options based on category capabilities if a category is provided
            if category:
                if source == ImportSource.PROJECT and not category.supports_project:
                    continue
                if source == ImportSource.FILE and not category.supports_file:
                    continue

            item = QListWidgetItem(source.display_name)
            item.setData(Qt.UserRole, source)
            self.list.addItem(item)

        # Select the first item by default if available
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def update_for_category(self, category: ImportCategory) -> None:
        """Slot called when a new category is selected in the CategoryPanel."""
        self._populate_sources(category)

    def _on_changed(self, row: int) -> None:
        item = self.list.item(row)
        if item:
            source: ImportSource = item.data(Qt.UserRole)
            self.source_changed.emit(source)