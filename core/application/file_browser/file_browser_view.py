from __future__ import annotations

import os
from typing import Optional, List
from PySide6.QtCore import QDir, QModelIndex, Qt, Signal, QStandardPaths
from PySide6.QtGui import QStandardItemModel, QStandardItem
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
    QInputDialog,
    QMessageBox,
    QMenu,
    QFrame,
    QLabel,
    QSizePolicy,
)

from core.application.file_browser.file_browser_controller import FileBrowserController
from core.settings.localization.translator import tr


class FileBrowserView(QWidget):
    """
    Componente reutilizável de exploração de arquivos com dois painéis à esquerda
    (atalhos do sistema e favoritos separados), com rolagem vertical independente.
    """

    file_selected = Signal(str)
    directory_changed = Signal(str)
    selection_accepted = Signal(list)

    def __init__(
            self,
            name_filters: Optional[List[str]] = None,
            selection_mode: QTreeView.SelectionMode = QTreeView.SelectionMode.SingleSelection,
            allow_folder_selection: bool = True,
            parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._name_filters = name_filters or []
        self._selection_mode = selection_mode
        self._allow_folder_selection = allow_folder_selection

        self._setup_model()
        self._setup_ui()
        self._connect_signals()

        self.set_directory(QDir.homePath())

    def _setup_model(self) -> None:
        self.model = QFileSystemModel(self)
        self.model.setFilter(
            QDir.Filter.AllDirs
            | QDir.Filter.Files
            | QDir.Filter.NoDotAndDotDot
        )
        self.model.setNameFilterDisables(False)
        self.model.setRootPath(QDir.rootPath())

        if self._name_filters:
            self.model.setNameFilters(self._name_filters)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # --------------------------------------------------------------
        # 1. Barra superior: Caminho, Botão Favoritos, Nova Pasta e Procurar
        # --------------------------------------------------------------
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(3)

        self.path_input = QLineEdit(self)
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText(tr("file_browser.current_directory_placeholder", "Diretório atual..."))

        self.btn_favorite = QPushButton(tr("file_browser.add_favorite", "Adicionar aos favoritos"), self)
        self.btn_favorite.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_new_folder = QPushButton(tr("file_browser.new_folder", "Nova pasta"), self)
        self.btn_new_folder.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_browse = QPushButton(tr("file_browser.browse", "Procurar..."), self)
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)

        path_layout.addWidget(self.path_input, stretch=1)
        path_layout.addWidget(self.btn_favorite)
        path_layout.addWidget(self.btn_new_folder)
        path_layout.addWidget(self.btn_browse)

        layout.addLayout(path_layout)

        # --------------------------------------------------------------
        # 2. Splitter central: Coluna Esquerda (2 Frames) + QTreeView
        # --------------------------------------------------------------
        main_splitter = QSplitter(Qt.Horizontal, self)

        # Container esquerdo dividido em dois frames (Superior e Inferior)
        left_container = QWidget(main_splitter)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        # --- Frame Superior: Atalhos do Sistema ---
        self.shortcuts_list = QListView(left_container)
        self.shortcuts_model = QStandardItemModel(self)
        self.shortcuts_list.setModel(self.shortcuts_model)
        self.shortcuts_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.shortcuts_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # --- Frame Inferior: Favoritos ---
        fav_container = QWidget(left_container)
        fav_layout = QVBoxLayout(fav_container)
        fav_layout.setContentsMargins(0, 0, 0, 0)
        fav_layout.setSpacing(2)

        fav_label = QLabel(tr("file_browser.favorites_title", "FAVORITOS"), fav_container)
        # Deixando o estilo do título alinhado com o padrão da interface
        fav_label.setStyleSheet("font-weight: bold; font-size: 11px; padding-left: 2px;")

        self.favorites_list = QListView(fav_container)
        self.favorites_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.favorites_model = QStandardItemModel(self)
        self.favorites_list.setModel(self.favorites_model)
        self.favorites_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.favorites_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        fav_layout.addWidget(fav_label)
        fav_layout.addWidget(self.favorites_list)

        # Divisor interno para ajustar proporção entre atalhos e favoritos à esquerda
        left_splitter = QSplitter(Qt.Vertical, left_container)
        left_splitter.addWidget(self.shortcuts_list)
        left_splitter.addWidget(fav_container)
        left_splitter.setSizes([220, 180])

        left_layout.addWidget(left_splitter)

        # Popula os modelos dos dois painéis
        self._populate_shortcuts()
        self._populate_favorites()

        # --- Visualizador principal de arquivos (Direita) ---
        self.tree_view = QTreeView(main_splitter)
        self.tree_view.setModel(self.model)
        self.tree_view.setSelectionMode(self._selection_mode)
        self.tree_view.setSelectionBehavior(QTreeView.SelectionBehavior.SelectItems)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSortingEnabled(True)

        self.tree_view.setColumnWidth(0, 260)
        self.tree_view.setColumnWidth(1, 90)
        self.tree_view.setColumnWidth(2, 100)
        self.tree_view.setColumnWidth(3, 140)

        main_splitter.setSizes([180, 420])
        layout.addWidget(main_splitter, stretch=1)

    def _populate_shortcuts(self) -> None:
        """Preenche o painel superior com os atalhos do sistema."""
        self.shortcuts_model.clear()
        self.shortcuts_map = {}

        locations = [
            ("file_browser.home", QStandardPaths.StandardLocation.HomeLocation),
            ("file_browser.documents", QStandardPaths.StandardLocation.DocumentsLocation),
            ("file_browser.downloads", QStandardPaths.StandardLocation.DownloadLocation),
            ("file_browser.pictures", QStandardPaths.StandardLocation.PicturesLocation),
            ("file_browser.desktop", QStandardPaths.StandardLocation.DesktopLocation),
            ("file_browser.music", QStandardPaths.StandardLocation.MusicLocation),
            ("file_browser.movies", QStandardPaths.StandardLocation.MoviesLocation),
        ]

        for key, loc_type in locations:
            paths = QStandardPaths.standardLocations(loc_type)
            if paths:
                path = paths[0]
                if QDir(path).exists():
                    name = tr(key, key.split('.')[-1].capitalize())
                    item = QStandardItem(name)
                    item.setEditable(False)
                    item.setData(path, Qt.ItemDataRole.UserRole)
                    self.shortcuts_model.appendRow(item)
                    self.shortcuts_map[name] = path

        root_name = tr("file_browser.root", "Raiz (/)")
        root_item = QStandardItem(root_name)
        root_item.setEditable(False)
        root_item.setData(QDir.rootPath(), Qt.ItemDataRole.UserRole)
        self.shortcuts_model.appendRow(root_item)
        self.shortcuts_map[root_name] = QDir.rootPath()

    def _populate_favorites(self) -> None:
        """Preenche o painel inferior com as pastas favoritas do JSON."""
        self.favorites_model.clear()
        self.favorites_map = {}

        favorites = FileBrowserController.load_favorites()
        if favorites:
            for fav_name, fav_path in favorites.items():
                if QDir(fav_path).exists():
                    item = QStandardItem(fav_name)
                    item.setEditable(False)
                    item.setData(fav_path, Qt.ItemDataRole.UserRole)
                    self.favorites_model.appendRow(item)
                    self.favorites_map[fav_name] = fav_path

    def _populate_sidebar(self) -> None:
        """Método auxiliar unificado para atualizar ambos os painéis."""
        self._populate_shortcuts()
        self._populate_favorites()

    def _connect_signals(self) -> None:
        self.btn_browse.clicked.connect(self._on_browse_clicked)
        self.btn_favorite.clicked.connect(self._on_add_favorite_clicked)
        self.btn_new_folder.clicked.connect(self._on_new_folder_clicked)
        self.tree_view.clicked.connect(self._on_item_clicked)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

        # Conexões da esquerda
        self.shortcuts_list.clicked.connect(self._on_shortcut_clicked)
        self.favorites_list.clicked.connect(self._on_favorite_clicked)
        self.favorites_list.customContextMenuRequested.connect(self._on_favorites_context_menu)

    def set_directory(self, directory: str) -> None:
        directory = QDir.cleanPath(directory)
        index = self.model.index(directory)
        if not index.isValid():
            return
        self.tree_view.setRootIndex(index)
        self.path_input.setText(directory)
        self.directory_changed.emit(directory)

    def current_directory(self) -> str:
        return self.path_input.text()

    def selected_file(self) -> Optional[str]:
        index = self.tree_view.currentIndex()
        if not index.isValid():
            return None
        return self.model.filePath(index)

    def selected_files(self) -> List[str]:
        paths = []
        for index in self.tree_view.selectionModel().selectedRows(0):
            if index.isValid():
                paths.append(self.model.filePath(index))
        return paths

    def _on_browse_clicked(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, tr("file_browser.select_directory_title", "Selecionar diretório"), self.current_directory()
        )
        if directory:
            self.set_directory(directory)

    def _on_add_favorite_clicked(self) -> None:
        current_dir = self.current_directory()
        selected = self.selected_file()

        target_path = selected if (selected and os.path.isdir(selected)) else current_dir
        if not target_path or not os.path.exists(target_path):
            QMessageBox.warning(
                self,
                tr("commons.warning", "Aviso"),
                tr("file_browser.invalid_folder_warning", "Selecione uma pasta válida para favoritar.")
            )
            return

        folder_name = os.path.basename(target_path) or target_path

        favorites = FileBrowserController.load_favorites()
        favorites[folder_name] = target_path
        FileBrowserController.save_favorites(favorites)

        self._populate_favorites()
        QMessageBox.information(
            self,
            tr("file_browser.success_title", "Sucesso"),
            tr("file_browser.favorite_added_msg", f"Pasta '{folder_name}' adicionada aos favoritos!").format(
                folder_name=folder_name)
        )

    def _on_new_folder_clicked(self) -> None:
        current_dir = self.current_directory()
        if not current_dir:
            return

        folder_name, ok = QInputDialog.getText(
            self,
            tr("file_browser.new_folder_title", "Nova Pasta"),
            tr("file_browser.new_folder_prompt", "Digite o nome da nova pasta:")
        )
        if ok and folder_name.strip():
            new_path = FileBrowserController.create_new_directory(current_dir, folder_name.strip())
            if new_path:
                self.set_directory(new_path)
            else:
                QMessageBox.critical(
                    self,
                    tr("commons.error", "Erro"),
                    tr("file_browser.create_folder_error", "Não foi possível criar a pasta.")
                )

    def _on_shortcut_clicked(self, index: QModelIndex) -> None:
        path = index.data(Qt.ItemDataRole.UserRole)
        if path and QDir(path).exists():
            self.set_directory(path)

    def _on_favorite_clicked(self, index: QModelIndex) -> None:
        path = index.data(Qt.ItemDataRole.UserRole)
        if path and QDir(path).exists():
            self.set_directory(path)

    def _on_item_clicked(self, index: QModelIndex) -> None:
        if not index.isValid():
            return
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.path_input.setText(path)
        self.file_selected.emit(path)

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        if not index.isValid():
            return
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.set_directory(path)
            return
        self.file_selected.emit(path)
        self.selection_accepted.emit([path])

    def _on_favorites_context_menu(self, position) -> None:
        """Exibe o menu de contexto apenas para o painel de favoritos."""
        index = self.favorites_list.indexAt(position)
        if not index.isValid():
            return

        name = index.data(Qt.ItemDataRole.DisplayRole)
        favorites = FileBrowserController.load_favorites()
        if name in favorites:
            menu = QMenu(self)
            remove_action = menu.addAction(tr("file_browser.remove_favorite", "Remover dos favoritos"))

            action = menu.exec(self.favorites_list.viewport().mapToGlobal(position))

            if action == remove_action:
                self._remove_favorite(name)

    def _remove_favorite(self, name: str) -> None:
        """Remove o favorito do JSON e atualiza o painel inferior."""
        favorites = FileBrowserController.load_favorites()
        if name in favorites:
            del favorites[name]
            FileBrowserController.save_favorites(favorites)
            self._populate_favorites()
            QMessageBox.information(
                self,
                tr("commons.success", "Sucesso"),
                tr("file_browser.favorite_removed", "Pasta removida dos favoritos.")
            )


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    browser = FileBrowserView(name_filters=["*.png", "*.jpg", "*.jpeg"])
    browser.resize(850, 520)
    browser.setWindowTitle("Componente Reutilizável - Painéis Independentes à Esquerda")
    browser.show()

    sys.exit(app.exec())