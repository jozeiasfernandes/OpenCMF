from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QDir, QModelIndex, Qt, Signal, QStandardPaths
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QFileSystemModel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTreeView,
    QListView,
    QVBoxLayout,
    QWidget,
    QSplitter,
)


class FileBrowserView(QWidget):
    """
    Explorador de arquivos integrado ao Import Manager, com barra lateral de locais do sistema.
    """

    file_selected = Signal(str)
    directory_changed = Signal(str)

    # Filtros por categoria.
    CATEGORY_FILTERS: dict[str, list[str]] = {
        "volume": ["*.dcm", "*.vti", "*.vtk", "*.nrrd", "*.nii", "*.nii.gz", "*.mhd", "*.mha"],
        "dicom": ["*.dcm", "DICOMDIR"],
        "photo": ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif", "*.tiff"],
        "mesh": ["*.stl", "*.obj", "*.ply", "*.off", "*.vtp", "*.vtk"],
        "implant": ["*.stl", "*.obj", "*.ply", "*.step", "*.stp", "*.iges", "*.igs"],
        "scan": ["*.stl", "*.obj", "*.ply", "*.vtp"],
    }

    def __init__(
            self,
            category_id: str,
            parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.category_id = category_id.strip().lower()

        self._setup_model()
        self._setup_ui()
        self._connect_signals()

        self.set_directory(QDir.homePath())

    def _setup_model(self) -> None:
        """Inicializa o modelo nativo do sistema de arquivos."""
        self.model = QFileSystemModel(self)
        self.model.setFilter(
            QDir.Filter.AllDirs
            | QDir.Filter.Files
            | QDir.Filter.NoDotAndDotDot
        )
        self.model.setNameFilterDisables(False)
        self.model.setRootPath(QDir.rootPath())
        self._apply_category_filters()

    def _setup_ui(self) -> None:
        """Cria e configura os componentes visuais, incluindo a barra lateral com pastas do sistema."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # --------------------------------------------------------------
        # Barra de caminho e botão procurar
        # --------------------------------------------------------------
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(5)

        self.path_input = QLineEdit(self)
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Diretório atual...")

        self.btn_browse = QPushButton("Procurar...", self)
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)

        path_layout.addWidget(self.path_input, stretch=1)
        path_layout.addWidget(self.btn_browse)

        layout.addLayout(path_layout)

        # --------------------------------------------------------------
        # Splitter principal: Barra Lateral (Locais do Sistema) + QTreeView (Arquivos)
        # --------------------------------------------------------------
        splitter = QSplitter(Qt.Horizontal, self)

        # 1. Barra Lateral de Atalhos Dinâmicos do Sistema
        self.sidebar_list = QListView(splitter)
        self.sidebar_list.setMaximumWidth(190)
        self.sidebar_list.setMinimumWidth(140)

        self.sidebar_model = QStandardItemModel(self)
        self.shortcuts: dict[str, str] = {}

        # Mapeando diretórios padrão do sistema via QStandardPaths
        locations = [
            ("Home", QStandardPaths.StandardLocation.HomeLocation),
            ("Documentos", QStandardPaths.StandardLocation.DocumentsLocation),
            ("Downloads", QStandardPaths.StandardLocation.DownloadLocation),
            ("Imagens", QStandardPaths.StandardLocation.PicturesLocation),
            ("Área de Trabalho", QStandardPaths.StandardLocation.DesktopLocation),
            ("Músicas", QStandardPaths.StandardLocation.MusicLocation),
            ("Vídeos", QStandardPaths.StandardLocation.MoviesLocation),
        ]

        for name, loc_type in locations:
            paths = QStandardPaths.standardLocations(loc_type)
            if paths:
                path = paths[0]
                if QDir(path).exists():
                    item = QStandardItem(name)
                    item.setEditable(False)
                    item.setData(path, Qt.ItemDataRole.UserRole)
                    self.sidebar_model.appendRow(item)
                    self.shortcuts[name] = path

        # Adicionar Raiz do sistema ao final
        root_item = QStandardItem("Raiz (/)")
        root_item.setEditable(False)
        root_item.setData(QDir.rootPath(), Qt.ItemDataRole.UserRole)
        self.sidebar_model.appendRow(root_item)
        self.shortcuts["Raiz (/)"] = QDir.rootPath()

        self.sidebar_list.setModel(self.sidebar_model)

        # 2. Explorador de Arquivos principal (QTreeView)
        self.tree_view = QTreeView(splitter)
        self.tree_view.setModel(self.model)
        self.tree_view.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        self.tree_view.setSelectionBehavior(QTreeView.SelectionBehavior.SelectItems)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSortingEnabled(True)

        self.tree_view.setColumnWidth(0, 260)
        self.tree_view.setColumnWidth(1, 90)
        self.tree_view.setColumnWidth(2, 100)
        self.tree_view.setColumnWidth(3, 140)

        splitter.setSizes([160, 440])
        layout.addWidget(splitter, stretch=1)

        # Botão de importação inferior
        self.btn_import = QPushButton("Importar", self)
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_import)

    def _connect_signals(self) -> None:
        """Conecta os sinais internos do componente."""
        self.btn_browse.clicked.connect(self._on_browse_clicked)
        self.tree_view.clicked.connect(self._on_item_clicked)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self.sidebar_list.clicked.connect(self._on_sidebar_clicked)

    def _apply_category_filters(self) -> None:
        """Aplica os filtros correspondentes à categoria atual."""
        filters = self._get_category_filters()
        self.model.setNameFilters(filters)

    def _get_category_filters(self) -> list[str]:
        """Retorna os filtros correspondentes à categoria."""
        category = self.category_id
        if "dicom" in category:
            return self.CATEGORY_FILTERS["dicom"]
        if "volume" in category:
            return self.CATEGORY_FILTERS["volume"]
        if "photo" in category or "fotografia" in category:
            return self.CATEGORY_FILTERS["photo"]
        if "mesh" in category or "malha" in category:
            return self.CATEGORY_FILTERS["mesh"]
        if "implant" in category or "implante" in category:
            return self.CATEGORY_FILTERS["implant"]
        if "scan" in category:
            return self.CATEGORY_FILTERS["scan"]
        return []

    def set_directory(self, directory: str) -> None:
        """Define o diretório exibido pelo explorador."""
        directory = QDir.cleanPath(directory)
        index = self.model.index(directory)
        if not index.isValid():
            return
        self.tree_view.setRootIndex(index)
        self.path_input.setText(directory)
        self.directory_changed.emit(directory)

    def current_directory(self) -> str:
        """Retorna o diretório atualmente visualizado."""
        return self.path_input.text()

    def _on_browse_clicked(self) -> None:
        """Abre o diálogo para seleção de diretório."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar diretório",
            self.current_directory(),
            QFileDialog.Option.ShowDirsOnly,
        )
        if directory:
            self.set_directory(directory)

    def _on_sidebar_clicked(self, index: QModelIndex) -> None:
        """Navega para a pasta do sistema selecionada na barra lateral."""
        path = index.data(Qt.ItemDataRole.UserRole)
        if path and QDir(path).exists():
            self.set_directory(path)

    def _on_item_clicked(self, index: QModelIndex) -> None:
        """Atualiza o caminho ou emite a seleção de arquivo."""
        if not index.isValid():
            return
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.path_input.setText(path)
            return
        self.file_selected.emit(path)

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        """Permite entrar em diretórios com duplo clique."""
        if not index.isValid():
            return
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.set_directory(path)
            return
        self.file_selected.emit(path)

    def set_category(self, category_id: str) -> None:
        """Altera a categoria de importação dinamicamente."""
        self.category_id = category_id.strip().lower()
        self._apply_category_filters()

    def selected_file(self) -> Optional[str]:
        """Retorna o arquivo atualmente selecionado."""
        index = self.tree_view.currentIndex()
        if not index.isValid() or self.model.isDir(index):
            return None
        return self.model.filePath(index)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Instancia o FileBrowserView com uma categoria de exemplo para teste
    view = FileBrowserView(category_id="dicom")
    view.resize(750, 480)
    view.setWindowTitle("Teste - FileBrowserView")
    view.show()

    # Conecta os sinais principais para validação no console
    view.file_selected.connect(lambda path: print(f"[Arquivo Selecionado]: {path}"))
    view.directory_changed.connect(lambda dir_path: print(f"[Diretório Alterado]: {dir_path}"))

    if hasattr(view, "btn_import"):
        view.btn_import.clicked.connect(
            lambda: print(f"[Ação]: Botão Importar clicado. Arquivo atual: {view.selected_file()}"))

    sys.exit(app.exec())