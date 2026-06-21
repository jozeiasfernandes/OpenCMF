from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.localization.translator import tr
from .tools_tab_service import ToolbarService


class ToolsTab(QtWidgets.QWidget):
    tools_changed = QtCore.Signal()

    def __init__(self, components_path: Path, get_name_callback, parent=None):
        super().__init__(parent)
        self.service = ToolbarService(components_path)
        self._get_name = get_name_callback

        self._setup_ui()
        self._load_toolbars_list()

        if self.combo_toolbar.count() > 0:
            self.combo_toolbar.setCurrentIndex(0)

    # --- UI Setup ---
    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        top_layout = QtWidgets.QHBoxLayout()

        self.combo_toolbar = QtWidgets.QComboBox()
        self.combo_toolbar.currentTextChanged.connect(self._on_toolbar_changed)

        btn_new = QtWidgets.QPushButton(tr("Criar Nova Toolbar"))
        btn_new.clicked.connect(self._create_new_toolbar)

        btn_delete = QtWidgets.QPushButton(tr("Excluir Toolbar"))
        btn_delete.setStyleSheet("color: red;")
        btn_delete.clicked.connect(self._delete_current_toolbar)

        top_layout.addWidget(QtWidgets.QLabel(tr("Toolbar:")))
        top_layout.addWidget(self.combo_toolbar, stretch=1)
        top_layout.addWidget(btn_new)
        top_layout.addWidget(btn_delete)
        main_layout.addLayout(top_layout)

        list_layout = QtWidgets.QHBoxLayout()
        self.list_all = QtWidgets.QListWidget()

        right_container = QtWidgets.QVBoxLayout()
        self.list_selected = QtWidgets.QListWidget()
        btn_add = QtWidgets.QPushButton(tr("Adicionar tools à toolbar atual"))
        btn_add.clicked.connect(self._add_selected_from_list_all)
        right_container.addWidget(self.list_selected)
        right_container.addWidget(btn_add)

        list_layout.addWidget(self.list_all)
        list_layout.addLayout(right_container)

        # Botões de mover
        move_buttons = QtWidgets.QVBoxLayout()
        btn_up = QtWidgets.QPushButton("▲")
        btn_down = QtWidgets.QPushButton("▼")
        btn_up.clicked.connect(lambda: self._move_item(-1))
        btn_down.clicked.connect(lambda: self._move_item(1))
        move_buttons.addStretch();
        move_buttons.addWidget(btn_up)
        move_buttons.addWidget(btn_down);
        move_buttons.addStretch()

        list_layout.addLayout(move_buttons)
        main_layout.addLayout(list_layout)

        self.list_all.itemDoubleClicked.connect(lambda item: self._transfer(item, self.list_selected))
        self.list_selected.itemDoubleClicked.connect(lambda item: self._transfer(item, self.list_all))

    # --- Lógica de UI ---
    def _load_toolbars_list(self):
        self.combo_toolbar.clear()
        for tb in self.service.get_all_toolbars():
            self.combo_toolbar.addItem(tb["name"], userData=tb["path"])

    def _on_toolbar_changed(self):
        toolbar_path = self.combo_toolbar.currentData()
        if not toolbar_path: return

        self.list_all.clear()
        self.list_selected.clear()

        selected_paths = self.service.load_selected_tools(toolbar_path)
        all_paths = self.service.get_all_tools()

        # Popular selecionados
        for path in selected_paths:
            item = QtWidgets.QListWidgetItem(self._get_name(path))
            item.setData(QtCore.Qt.UserRole, path)
            self.list_selected.addItem(item)

        # Popular disponíveis (não selecionados)
        for path in all_paths:
            if path not in selected_paths:
                item = QtWidgets.QListWidgetItem(self._get_name(path))
                item.setData(QtCore.Qt.UserRole, path)
                self.list_all.addItem(item)

    def _transfer(self, item, target_list):
        source_list = self.list_all if target_list is self.list_selected else self.list_selected
        source_list.takeItem(source_list.row(item))
        target_list.addItem(item)
        self._save_state()

    def _add_selected_from_list_all(self):
        if item := self.list_all.currentItem():
            self._transfer(item, self.list_selected)

    def _move_item(self, direction):
        row = self.list_selected.currentRow()
        if row < 0: return
        new_row = row + direction
        if 0 <= new_row < self.list_selected.count():
            item = self.list_selected.takeItem(row)
            self.list_selected.insertItem(new_row, item)
            self.list_selected.setCurrentRow(new_row)
            self._save_state()

    def _save_state(self):
        toolbar_path = self.combo_toolbar.currentData()
        tools = [self.list_selected.item(i).data(QtCore.Qt.UserRole)
                 for i in range(self.list_selected.count())]
        self.service.save_toolbar_config(toolbar_path, tools)
        self.tools_changed.emit()

    def _create_new_toolbar(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Nova", "Nome da Toolbar:")
        if ok and name:
            try:
                self.service.create_toolbar(name)
                self._load_toolbars_list()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erro", str(e))

    def _delete_current_toolbar(self):
        path = self.combo_toolbar.currentData()
        if path and QtWidgets.QMessageBox.question(self, "Excluir", "Confirmar exclusão?") == QtWidgets.QMessageBox.Yes:
            self.service.delete_toolbar(path)
            self._load_toolbars_list()
            self.tools_changed.emit()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    components_path = Path("./core/components").resolve()
    def get_name(path):
        return path.stem.replace("_", " ").title()
    window = ToolsTab(components_path, get_name)
    window.setWindowTitle("Teste da Aba Tools")
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())