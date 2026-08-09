from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class CatalogView(QWidget):
    """Fase 4: Catálogo Online / Biblioteca 3D (CatalogView).
    Ativa-se para categorias de Malhas 3D Online e Implantes Dentários/Faciais[cite: 2]."""

    item_selected = Signal(object)
    download_requested = Signal(object)

    def __init__(self, category_id: str, parent=None):
        super().__init__(parent)
        self.category_id = category_id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        self.catalog_label = QLabel(f"Catálogo Online / Biblioteca 3D (Categoria: {category_id})[cite: 2]")
        self.catalog_label.setAlignment(Qt.AlignCenter)
        self.catalog_label.setStyleSheet("background-color: #2b2b2b; color: #ffffff; border-radius: 4px; padding: 20px;")
        layout.addWidget(self.catalog_label)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    view = CatalogView(category_id="mesh_online")
    view.resize(600, 400)
    view.show()

    sys.exit(app.exec())