from pathlib import Path
from PySide6 import QtWidgets, QtCore
from settings.localization.translator import tr
from components_loaders.tools_tab_loaders.tools_tab_service_loaders import ToolbarService


class ToolsTab(QtWidgets.QWidget):
    tools_changed = QtCore.Signal()

    def __init__(self, components_path: Path, get_name_callback=None, parent=None):
        super().__init__(parent)
        self.service = ToolbarService(components_path)
        self._get_name = get_name_callback
        self._setup_ui()
        self._load_toolbars_list()
        if self.combo_toolbar.count() > 0:
            self.combo_toolbar.setCurrentIndex(0)

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Topo
        top_layout = QtWidgets.QHBoxLayout()
        self.combo_toolbar = QtWidgets.QComboBox()
        self.combo_toolbar.currentIndexChanged.connect(self._on_toolbar_changed)

        btn_new = QtWidgets.QPushButton(tr("Criar Nova Toolbar"))
        btn_new.clicked.connect(self._create_new_toolbar)

        btn_delete = QtWidgets.QPushButton(tr("Excluir Toolbar"))
        btn_delete.setStyleSheet("colors: red;")
        btn_delete.clicked.connect(self._delete_current_toolbar)

        top_layout.addWidget(QtWidgets.QLabel(tr("Toolbar:")))
        top_layout.addWidget(self.combo_toolbar, stretch=1)
        top_layout.addWidget(btn_new)
        top_layout.addWidget(btn_delete)

        main_layout.addLayout(top_layout)

        # Área de Listagem com Splitter para redimensionamento
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        self.tree_all = QtWidgets.QTreeWidget()
        self.tree_all.setHeaderHidden(True)
        self.tree_all.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        right_container_widget = QtWidgets.QWidget()
        right_container = QtWidgets.QVBoxLayout(right_container_widget)
        right_container.setContentsMargins(0, 0, 0, 0)

        self.list_selected = QtWidgets.QListWidget()
        self.list_selected.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        btn_add = QtWidgets.QPushButton(tr("Adicionar"))
        btn_add.clicked.connect(self._add_selected_from_tree)

        btn_remove = QtWidgets.QPushButton(tr("Remover"))
        btn_remove.clicked.connect(self._remove_selected_tool)

        btn_remove_all = QtWidgets.QPushButton(tr("Remover Tudo"))
        btn_remove_all.clicked.connect(self._remove_all_tools)

        btn_save = QtWidgets.QPushButton(tr("Salvar Alterações"))
        btn_save.setStyleSheet("background-colors: #27ae60; colors: white;")
        btn_save.clicked.connect(self._save_state)

        right_container.addWidget(self.list_selected)
        right_container.addWidget(btn_add)
        right_container.addWidget(btn_remove)
        right_container.addWidget(btn_remove_all)
        right_container.addWidget(btn_save)

        splitter.addWidget(self.tree_all)
        splitter.addWidget(right_container_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        self.tree_all.itemDoubleClicked.connect(self._add_selected_from_tree)
        self.list_selected.itemDoubleClicked.connect(self._remove_selected_tool)

    def _load_toolbars_list(self):
        self.combo_toolbar.blockSignals(True)
        self.combo_toolbar.clear()
        for tb in self.service.get_all_toolbars():
            self.combo_toolbar.addItem(tb["name"], userData=tb["path"])
        self.combo_toolbar.blockSignals(False)

    def _on_toolbar_changed(self):
        toolbar_path = self.combo_toolbar.currentData()
        if not toolbar_path:
            self.tree_all.clear()
            self.list_selected.clear()
            return

        self.tree_all.clear()
        self.list_selected.clear()

        selected_paths = self.service.load_selected_tools(toolbar_path)
        all_tools_meta = self.service.get_all_tools_with_metadata()

        categories = {}
        for tool in all_tools_meta:
            path = tool["path"]
            display_name = self._get_name(tool) if self._get_name else tool["display_name"]

            if path in selected_paths:
                item = QtWidgets.QListWidgetItem(display_name)
                item.setData(QtCore.Qt.UserRole, path)
                self.list_selected.addItem(item)
            else:
                cat_name = tool["category"].name
                if cat_name not in categories:
                    parent = QtWidgets.QTreeWidgetItem(self.tree_all, [cat_name])
                    parent.setExpanded(True)
                    categories[cat_name] = parent

                child = QtWidgets.QTreeWidgetItem(categories[cat_name], [display_name])
                child.setData(0, QtCore.Qt.UserRole, path)

    def _add_selected_from_tree(self):
        selected_items = self.tree_all.selectedItems()
        for item in selected_items:
            if item.parent():
                path = item.data(0, QtCore.Qt.UserRole)
                name = item.text(0)

                item.parent().removeChild(item)

                new_item = QtWidgets.QListWidgetItem(name)
                new_item.setData(QtCore.Qt.UserRole, path)
                self.list_selected.addItem(new_item)

    def _remove_selected_tool(self):
        for current_item in self.list_selected.selectedItems():
            self.list_selected.takeItem(self.list_selected.row(current_item))
        # Recarrega limpo chamando o estado atual do combo sem perder as alterações não salvas
        toolbar_path = self.combo_toolbar.currentData()
        if toolbar_path:
            # Opcional: Para simplificar e garantir consistência sem recriar tudo da árvore do zero,
            # podemos apenas chamar _on_toolbar_changed se preferir forçar o reload do arquivo,
            # mas o ideal para edição em memória é simplesmente remover da lista selecionada.
            pass

    def _remove_selected_tool(self):
        current_item = self.list_selected.currentItem()
        if current_item:
            self.list_selected.takeItem(self.list_selected.row(current_item))


    def _remove_all_tools(self):
        self.list_selected.clear()

    def _save_state(self):
        toolbar_path = self.combo_toolbar.currentData()
        if not toolbar_path:
            return

        tools = [self.list_selected.item(i).data(QtCore.Qt.UserRole) for i in range(self.list_selected.count())]
        self.service.save_toolbar_config(toolbar_path, tools)
        self.tools_changed.emit()
        QtWidgets.QMessageBox.information(self, "Sucesso", "Configuração salva!")

    def _create_new_toolbar(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Nova", "Nome da Toolbar:")
        if ok and name:
            try:
                self.service.create_toolbar(name)
                self._load_toolbars_list()
                if self.combo_toolbar.count() > 0:
                    self.combo_toolbar.setCurrentIndex(self.combo_toolbar.count() - 1)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erro", str(e))

    def _delete_current_toolbar(self):
        path = self.combo_toolbar.currentData()
        if path and QtWidgets.QMessageBox.question(self, "Excluir", "Confirmar exclusão?") == QtWidgets.QMessageBox.Yes:
            self.service.delete_toolbar(path)
            self._load_toolbars_list()
            self.tools_changed.emit()

