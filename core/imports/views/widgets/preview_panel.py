from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.settings.localization.translator import tr


class PreviewPanel(QWidget):
    """
    Painel responsável pela visualização prévia
    dos objetos selecionados no Gestor de Imports.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None
    ) -> None:

        super().__init__(parent)

        self._current_item = None

        self._setup_ui()
        self._create_views()


    def _setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )


        self.header_label = QLabel(
            tr(
                "import.panels.preview",
                "Pré-visualização"
            )
        )

        layout.addWidget(
            self.header_label
        )


        self.stack = QStackedWidget()

        layout.addWidget(
            self.stack
        )


    def _create_views(self):

        self.empty_view = self._create_placeholder(
            "Nenhum item selecionado."
        )

        self.mesh_view = self._create_placeholder(
            "Preview de Malha 3D"
        )

        self.volume_view = self._create_placeholder(
            "Preview de Volume"
        )

        self.image_view = self._create_placeholder(
            "Preview de Imagem"
        )


        self.stack.addWidget(
            self.empty_view
        )

        self.stack.addWidget(
            self.mesh_view
        )

        self.stack.addWidget(
            self.volume_view
        )

        self.stack.addWidget(
            self.image_view
        )


        self.stack.setCurrentWidget(
            self.empty_view
        )


    def _create_placeholder(
        self,
        text: str
    ) -> QWidget:

        widget = QWidget()

        layout = QVBoxLayout(widget)

        label = QLabel(text)

        label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            label
        )

        return widget


    def update_preview(
        self,
        item: Optional[object]
    ):

        self._current_item = item


        if item is None:

            self.stack.setCurrentWidget(
                self.empty_view
            )

            return


        item_type = self._detect_type(item)


        if item_type == "mesh":

            self.stack.setCurrentWidget(
                self.mesh_view
            )

        elif item_type == "volume":

            self.stack.setCurrentWidget(
                self.volume_view
            )

        elif item_type == "image":

            self.stack.setCurrentWidget(
                self.image_view
            )


    def _detect_type(self, item):

        """
        Futuramente substituir por
        sistema de tipos do Core.
        """

        return getattr(
            item,
            "type",
            None
        )