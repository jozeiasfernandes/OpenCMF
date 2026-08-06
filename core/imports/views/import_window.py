from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QSplitter,
)

from core.imports.models.import_category import ImportCategory
from core.imports.models.import_source import ImportSource
from core.imports.views.widgets.category_panel import CategoryPanel
from core.imports.views.widgets.content_panel import ContentPanel
from core.imports.views.widgets.preview_panel import PreviewPanel
from core.imports.views.widgets.source_panel import SourcePanel
from core.settings.localization.translator import tr


class ImportWindow(QMainWindow):
    """Main Import Window orchestrating categories, sources, content browser,
    and preview panels.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        self.setWindowTitle(tr("import.window_title", "Importador de Objetos - OpenCMF"))
        self.resize(1100, 700)

        # Central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Splitters layout structure
        # Left side: Categories & Sources
        left_splitter = QSplitter(Qt.Vertical)
        self.category_panel = CategoryPanel()
        self.source_panel = SourcePanel()
        left_splitter.addWidget(self.category_panel)
        left_splitter.addWidget(self.source_panel)
        left_splitter.setSizes([350, 350])

        # Right side: Content Browser & Preview
        right_splitter = QSplitter(Qt.Vertical)
        self.content_panel = ContentPanel()
        self.preview_panel = PreviewPanel()
        right_splitter.addWidget(self.content_panel)
        right_splitter.addWidget(self.preview_panel)
        right_splitter.setSizes([450, 250])

        # Master horizontal splitter
        master_splitter = QSplitter(Qt.Horizontal)
        master_splitter.addWidget(left_splitter)
        master_splitter.addWidget(right_splitter)
        master_splitter.setSizes([350, 750])

        main_layout.addWidget(master_splitter)

        # Bottom Action Bar (Import button)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.import_button = QPushButton(tr("import.btn.import_objects", "Importar Objetos"))
        self.import_button.setEnabled(False)  # Enabled later when valid selection is made
        bottom_layout.addWidget(self.import_button)

        main_layout.addLayout(bottom_layout)

    def _connect_signals(self) -> None:
        # Category panel changes update the source panel and content panel
        self.category_panel.category_changed.connect(self.source_panel.update_for_category)
        self.category_panel.category_changed.connect(self.content_panel.update_category)

        # Source panel changes update the content panel
        self.source_panel.source_changed.connect(self.content_panel.update_source)

        # Content panel item selection updates the preview panel and action button
        self.content_panel.item_selected.connect(self.preview_panel.update_preview)
        self.content_panel.item_selected.connect(self._on_item_selected)

    def _on_item_selected(self, item: Optional[object]) -> None:
        """Enable or disable the import button based on whether an item is selected."""
        self.import_button.setEnabled(item is not None)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ImportWindow()
    window.show()
    sys.exit(app.exec())