from __future__ import annotations

from typing import Optional, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTreeView,
    QWidget
)

from core.application.file_browser.file_browser_view import FileBrowserView


class FileBrowserDialog(QDialog):
    """
    Diálogo modal reutilizável contendo o FileBrowserView,
    com botões de confirmação (Abrir/Selecionar) e cancelamento.
    """

    files_selected = Signal(list)

    def __init__(
            self,
            title: str = "Selecionar Arquivo",
            name_filters: Optional[List[str]] = None,
            selection_mode: QTreeView.SelectionMode = QTreeView.SelectionMode.SingleSelection,
            allow_folder_selection: bool = False,
            parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle(title)
        self.resize(750, 480)

        self._setup_ui(name_filters, selection_mode, allow_folder_selection)

    def _setup_ui(
            self,
            name_filters: Optional[List[str]],
            selection_mode: QTreeView.SelectionMode,
            allow_folder_selection: bool,
    ) -> None:
        """Configura o layout do diálogo."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Instancia o componente central de visualização
        self.browser_view = FileBrowserView(
            name_filters=name_filters,
            selection_mode=selection_mode,
            allow_folder_selection=allow_folder_selection,
            parent=self,
        )
        layout.addWidget(self.browser_view, stretch=1)

        # Botões de Ação Inferiores (Cancelar / Confirmar)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar", self)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_select = QPushButton("Selecionar", self)
        self.btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select.setDefault(True)
        self.btn_select.clicked.connect(self._on_select_clicked)

        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_select)

        layout.addLayout(button_layout)

        # Conecta o duplo clique do browser para aceitar o diálogo automaticamente em seleção única
        self.browser_view.selection_accepted.connect(self._on_selection_accepted)

    def _on_select_clicked(self) -> None:
        """Trata o clique no botão de confirmação."""
        files = self.browser_view.selected_files()

        # Se nenhum arquivo foi explicitamente selecionado, mas permitimos seleção de pastas,
        # podemos pegar o diretório atual exibido na barra de caminhos.
        if not files and getattr(self.browser_view, "_allow_folder_selection", False):
            current_dir = self.browser_view.current_directory()
            if current_dir:
                files = [current_dir]

        if not files:
            single = self.browser_view.selected_file()
            if single:
                files = [single]

        if files:
            self.files_selected.emit(files)
            self.accept()

    def _on_selection_accepted(self, files: List[str]) -> None:
        """Trata o evento de seleção rápida (duplo clique)."""
        if files:
            self.files_selected.emit(files)
            self.accept()

    def get_selected_files(self) -> List[str]:
        """Método utilitário para recuperar os arquivos selecionados após fechar o diálogo."""
        return self.browser_view.selected_files()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dialog = FileBrowserDialog(
        title="Teste - Diálogo de Arquivos",
        name_filters=["*.png", "*.jpg", "*.jpeg"]
    )

    dialog.files_selected.connect(lambda files: print(f"Arquivos confirmados: {files}"))

    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("Diálogo aceito com sucesso!")
    else:
        print("Diálogo cancelado.")

    sys.exit(0)