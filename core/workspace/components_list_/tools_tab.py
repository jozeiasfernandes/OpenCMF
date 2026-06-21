from pathlib import Path
from PySide6 import QtWidgets, QtCore


class ToolsTab(QtWidgets.QWidget):
    tools_changed = QtCore.Signal()

    def __init__(self, components_path: Path, get_name_callback, parent=None):
        super().__init__(parent)
        self.toolbars_path = components_path / "toolbars"
        self.tools_path = components_path / "tools"
        self._get_name = get_name_callback
        self._setup_ui()
        self._load_toolbars()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        self.combo_toolbar = QtWidgets.QComboBox()
        self.combo_toolbar.currentTextChanged.connect(self._on_toolbar_changed)
        main_layout.addWidget(QtWidgets.QLabel("Selecione a Toolbar:"))
        main_layout.addWidget(self.combo_toolbar)

        # Layout das listas
        list_layout = QtWidgets.QHBoxLayout()
        self.list_all = QtWidgets.QListWidget()
        self.list_selected = QtWidgets.QListWidget()

        buttons = QtWidgets.QVBoxLayout()
        btn_up = QtWidgets.QPushButton("▲")
        btn_down = QtWidgets.QPushButton("▼")
        btn_up.clicked.connect(lambda: self.move_item(-1))
        btn_down.clicked.connect(lambda: self.move_item(1))
        buttons.addStretch()
        buttons.addWidget(btn_up)
        buttons.addWidget(btn_down)
        buttons.addStretch()

        self.list_all.itemDoubleClicked.connect(
            lambda item: self.transfer(item, self.list_selected)
        )
        self.list_selected.itemDoubleClicked.connect(
            lambda item: self.transfer(item, self.list_all)
        )

        self.list_all.itemChanged.connect(self._on_item_changed)
        self.list_selected.itemChanged.connect(self._on_item_changed)

        list_layout.addWidget(self.list_all)
        list_layout.addWidget(self.list_selected)
        list_layout.addLayout(buttons)

        main_layout.addLayout(list_layout)

    def _load_toolbars(self):
        if not self.toolbars_path.exists():
            return

        toolbars = [f.stem for f in self.toolbars_path.glob("*.py") if f.name != "__init__.py"]
        self.combo_toolbar.addItems(sorted(toolbars))

    def _on_toolbar_changed(self, text):
        self.list_all.clear()
        self.list_selected.clear()
        self._load_tools()

    def _load_tools(self):
        if not self.tools_path.exists():
            return

        for path in sorted(self.tools_path.glob("*.py")):
            if path.name == "__init__.py":
                continue

            item = QtWidgets.QListWidgetItem(self._get_name(path))
            item.setData(QtCore.Qt.UserRole, path)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.list_all.addItem(item)

    def _on_item_changed(self, item):
        self.list_all.blockSignals(True)
        self.list_selected.blockSignals(True)

        if item.checkState() == QtCore.Qt.Checked:
            if item.listWidget() is self.list_all:
                self.list_all.takeItem(self.list_all.row(item))
                self.list_selected.addItem(item)
        else:
            if item.listWidget() is self.list_selected:
                self.list_selected.takeItem(self.list_selected.row(item))
                self.list_all.addItem(item)

        self.list_all.blockSignals(False)
        self.list_selected.blockSignals(False)
        self.tools_changed.emit()

    def transfer(self, item, target):
        source = self.list_all if target is self.list_selected else self.list_selected
        source.takeItem(source.row(item))
        target.addItem(item)
        item.setCheckState(QtCore.Qt.Checked if target is self.list_selected else QtCore.Qt.Unchecked)
        self.tools_changed.emit()

    def move_item(self, direction):
        row = self.list_selected.currentRow()
        if row < 0: return
        new_row = row + direction
        if not (0 <= new_row < self.list_selected.count()): return
        item = self.list_selected.takeItem(row)
        self.list_selected.insertItem(new_row, item)
        self.list_selected.setCurrentRow(new_row)
        self.tools_changed.emit()

    def selected_tools(self):
        return [self.list_selected.item(i).data(QtCore.Qt.UserRole) for i in range(self.list_selected.count())]

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    tools_path = Path("./core/components/tools")

    def get_name(path):
        return path.stem.replace("_", " ").title()

    window = ToolsTab(tools_path, get_name)
    window.setWindowTitle("Teste da Aba Tools")
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())