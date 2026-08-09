from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ProjectItemsView(QWidget):
    """Fase 2: Visualização de Itens do Projeto (ProjectItemsView).
    Seção superior para listagem de itens e inferior para preview/fatiamento[cite: 2]."""

    item_selected = Signal(object)
    import_confirmed = Signal(object)

    def __init__(self, category_id: str, parent=None):
        super().__init__(parent)
        self.category_id = category_id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # Placeholder para o Frame Superior (Listagem / Grid)[cite: 2]
        self.top_label = QLabel(f"Volumes atuais do projeto (Categoria: {category_id})")
        self.top_label.setAlignment(Qt.AlignCenter)
        self.top_label.setStyleSheet("background-color: #2b2b2b; color: #ffffff; border-radius: 4px; padding: 20px;")
        layout.addWidget(self.top_label, stretch=2)

        # Placeholder para o Frame Inferior (Preview / Fatiamento / Informações)[cite: 2]
        self.bottom_label = QLabel("Preview: [SLICE]")
        self.bottom_label.setAlignment(Qt.AlignCenter)
        self.bottom_label.setStyleSheet("background-color: #2b2b2b; color: #cccccc; border-radius: 4px; padding: 20px;")
        layout.addWidget(self.bottom_label, stretch=3)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    view = ProjectItemsView(category_id="volume_dicom")
    view.resize(600, 500)
    view.show()

    sys.exit(app.exec())