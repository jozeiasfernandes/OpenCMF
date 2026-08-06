from typing import Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.imports.models.import_category import ImportCategory
from core.imports.models.import_source import ImportSource
from core.settings.localization.translator import tr


class ContentPanel(QWidget):
    """
    Painel responsável por exibir o conteúdo de importação.

    Dependendo da categoria e origem selecionadas,
    apresenta:
        - Galeria do projeto
        - Navegador de arquivos
        - Biblioteca online
        - Outros navegadores específicos
    """

    item_selected = Signal(object)

    def __init__(
        self,
        parent: Optional[QWidget] = None
    ) -> None:

        super().__init__(parent)

        self._current_category: Optional[ImportCategory] = None
        self._current_source: Optional[ImportSource] = None

        self._setup_ui()
        self._create_views()

    # ---------------------------------------------------------
    # Interface
    # ---------------------------------------------------------

    def _setup_ui(self) -> None:

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.header_label = QLabel(
            tr(
                "import.panels.content",
                "Browser / Galeria"
            )
        )

        layout.addWidget(
            self.header_label
        )


        self.stack = QStackedWidget()

        layout.addWidget(
            self.stack
        )


    def _create_views(self) -> None:
        """
        Criação das páginas internas.
        Inicialmente placeholders.
        """

        self.empty_view = self._create_placeholder(
            "Selecione uma categoria e uma origem."
        )

        self.project_view = self._create_placeholder(
            "Galeria do Projeto"
        )

        self.file_view = self._create_placeholder(
            "Navegador de Arquivos"
        )

        self.online_view = self._create_placeholder(
            "Biblioteca Online"
        )


        self.stack.addWidget(
            self.empty_view
        )

        self.stack.addWidget(
            self.project_view
        )

        self.stack.addWidget(
            self.file_view
        )

        self.stack.addWidget(
            self.online_view
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


    # ---------------------------------------------------------
    # Atualização de estado
    # ---------------------------------------------------------

    def update_category(
        self,
        category: ImportCategory
    ) -> None:

        self._current_category = category

        self._refresh()


    def update_source(
        self,
        source: ImportSource
    ) -> None:

        self._current_source = source

        self._refresh()


    def update_content(
        self,
        category: ImportCategory,
        source: ImportSource
    ) -> None:

        self._current_category = category
        self._current_source = source

        self._refresh()


    # ---------------------------------------------------------
    # Controle das páginas
    # ---------------------------------------------------------

    def _refresh(self) -> None:

        if (
            self._current_category is None
            or self._current_source is None
        ):
            self._show_empty()
            return


        source = self._current_source


        if source == ImportSource.PROJECT:

            self.header_label.setText(
                tr(
                    "import.project.gallery",
                    "Galeria do Projeto"
                )
            )

            self.stack.setCurrentWidget(
                self.project_view
            )


        elif source == ImportSource.FILE:

            self.header_label.setText(
                tr(
                    "import.file.browser",
                    "Navegador de Arquivos"
                )
            )

            self.stack.setCurrentWidget(
                self.file_view
            )


        elif source == ImportSource.ONLINE:

            self.header_label.setText(
                tr(
                    "import.online.library",
                    "Biblioteca Online"
                )
            )

            self.stack.setCurrentWidget(
                self.online_view
            )


    def _show_empty(self) -> None:

        self.header_label.setText(
            tr(
                "import.content.empty",
                "Browser / Galeria"
            )
        )

        self.stack.setCurrentWidget(
            self.empty_view
        )