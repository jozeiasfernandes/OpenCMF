import importlib.util
import json
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.localization.translator import get_base_dir, tr


class ToolsTab(QtWidgets.QWidget):
    tools_changed = QtCore.Signal()

    def __init__(self, components_path: Path, get_name_callback, parent=None):
        super().__init__(parent)
        self.components_path = components_path
        self.toolbars_path = components_path / "toolbars"
        self.tools_path = components_path / "tools"
        self._get_name = get_name_callback

        self._setup_ui()
        self._load_toolbars()

        if self.combo_toolbar.count() > 0:
            self.combo_toolbar.setCurrentIndex(0)

    # --- Setup da UI ---
    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        top_layout = QtWidgets.QHBoxLayout()

        self.combo_toolbar = QtWidgets.QComboBox()
        self.combo_toolbar.currentTextChanged.connect(self._on_toolbar_changed)

        btn_new_toolbar = QtWidgets.QPushButton(tr("Criar Nova Toolbar"))
        btn_new_toolbar.clicked.connect(self._create_new_toolbar)

        btn_delete_toolbar = QtWidgets.QPushButton(tr("Excluir Toolbar"))
        btn_delete_toolbar.setStyleSheet("color: red;")
        btn_delete_toolbar.clicked.connect(self._delete_current_toolbar)

        top_layout.addWidget(QtWidgets.QLabel(tr("Toolbar:")))
        top_layout.addWidget(self.combo_toolbar, stretch=1)
        top_layout.addWidget(btn_new_toolbar)
        top_layout.addWidget(btn_delete_toolbar)

        main_layout.addLayout(top_layout)

        list_layout = QtWidgets.QHBoxLayout()
        self.list_all = QtWidgets.QListWidget()
        self.list_selected = QtWidgets.QListWidget()

        btn_add = QtWidgets.QPushButton(tr("Adicionar tools"))
        btn_add.clicked.connect(self._add_selected_from_list_all)

        buttons = QtWidgets.QVBoxLayout()
        btn_up = QtWidgets.QPushButton("▲")
        btn_down = QtWidgets.QPushButton("▼")
        btn_up.clicked.connect(lambda: self.move_item(-1))
        btn_down.clicked.connect(lambda: self.move_item(1))
        buttons.addStretch()
        buttons.addWidget(btn_up)
        buttons.addWidget(btn_down)
        buttons.addStretch()


        buttons.addWidget(btn_add)  # Adicione antes dos botões de cima/baixo
        buttons.addWidget(btn_up)
        buttons.addWidget(btn_down)

        self.list_all.itemDoubleClicked.connect(lambda item: self.transfer(item, self.list_selected))
        self.list_selected.itemDoubleClicked.connect(lambda item: self.transfer(item, self.list_all))
        self.list_all.itemChanged.connect(self._on_item_changed)
        self.list_selected.itemChanged.connect(self._on_item_changed)

        list_layout.addWidget(self.list_all)
        list_layout.addWidget(self.list_selected)
        list_layout.addLayout(buttons)
        main_layout.addLayout(list_layout)

    # --- Gerenciamento de Toolbar (CRUD) ---
    def _create_new_toolbar(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Nova Toolbar", "Nome da Toolbar:")
        if not (ok and name): return

        class_name = name.replace(" ", "").capitalize()
        file_name = name.lower().replace(" ", "_") + ".py"
        object_name = file_name.replace(".py", "")
        file_path = self.toolbars_path / file_name

        if file_path.exists():
            QtWidgets.QMessageBox.warning(self, "Erro", "Já existe uma toolbar com este nome.")
            return

        template_path = self.components_path.parent / "workspace" / "components_list_" / "toolbar_template.py"
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = content.replace("{class_name}", class_name)
            content = content.replace("{name}", name)
            content = content.replace("{object_name}", object_name)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.combo_toolbar.clear()
            self._load_toolbars()

        except Exception as e:
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(self, "Erro", f"Falha ao criar template: {str(e)}")

    def _delete_current_toolbar(self):
        file_path = self.combo_toolbar.currentData()
        if not file_path or not isinstance(file_path, Path): return

        reply = QtWidgets.QMessageBox.question(self, "Excluir Toolbar",
                                               f"Deseja realmente excluir a toolbar '{self.combo_toolbar.currentText()}'?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                for suffix in [".py", ".png", ".json"]:
                    p = file_path.with_suffix(suffix)
                    if p.exists(): p.unlink()

                self.combo_toolbar.blockSignals(True)
                self.combo_toolbar.clear()
                self._load_toolbars()
                self.combo_toolbar.blockSignals(False)
                self.tools_changed.emit()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erro", f"Falha ao excluir: {e}")

    # --- Carregamento e Persistência ---
    def _add_selected_from_list_all(self):
        toolbar_path = self.combo_toolbar.currentData()
        if not toolbar_path:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione uma toolbar primeiro.")
            return

        self._save_selected_tools(toolbar_path)
        self.tools_changed.emit()

        QtWidgets.QMessageBox.information(self, "Sucesso",
                                          f"Ferramentas aplicadas na toolbar '{self.combo_toolbar.currentText()}'.")

    def _load_toolbars(self):
        if not self.toolbars_path.exists(): return
        self.combo_toolbar.clear()
        for path in sorted(self.toolbars_path.glob("*.py")):
            if path.name != "__init__.py":
                abs_path = path.resolve()
                self.combo_toolbar.addItem(self._obter_nome_toolbar(abs_path), userData=abs_path)

    def _load_tools(self, exclude_paths=None):
        exclude_paths = exclude_paths or []
        if not self.tools_path.exists(): return

        for path in sorted(self.tools_path.glob("*.py")):
            if path.name != "__init__.py" and path not in exclude_paths:
                item = QtWidgets.QListWidgetItem(self._get_name(path))
                item.setData(QtCore.Qt.UserRole, path)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                self.list_all.addItem(item)

    def _load_selected_tools(self, toolbar_path: Path):
        json_path = toolbar_path.with_suffix(".json")
        if not json_path.exists():
            return []

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            full_paths = []
            for item in data:
                full_path = self.components_path / item
                full_paths.append(full_path)

            return full_paths
        except:
            return []

    def _save_selected_tools(self, toolbar_path: Path) -> None:
        # Resolve o caminho para absoluto antes de qualquer operação
        abs_toolbar_path = toolbar_path.resolve()
        json_path = abs_toolbar_path.with_suffix(".json")

        # Garante que a pasta existe
        json_path.parent.mkdir(parents=True, exist_ok=True)

        # Coleta as ferramentas
        tools = [self.list_selected.item(i).data(QtCore.Qt.UserRole)
                 for i in range(self.list_selected.count())]

        # Salva o caminho absoluto real no disco
        absolute_paths = [str(Path(p).resolve()) for p in filter(None, tools)]

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(absolute_paths, f, indent=4, ensure_ascii=False)

            # Debug visual no console
            print(f"DEBUG: JSON gravado fisicamente em: {json_path}")

        except Exception as e:
            print(f"ERRO AO SALVAR JSON: {e}")

    # --- Lógica de UI e Interação ---
    def _on_toolbar_changed(self, text):
        self.list_all.blockSignals(True)
        self.list_selected.blockSignals(True)
        self.list_all.clear()
        self.list_selected.clear()

        toolbar_path = self.combo_toolbar.currentData()
        if toolbar_path:
            saved = self._load_selected_tools(toolbar_path)
            self._load_tools(exclude_paths=saved)
            for path in saved:
                if path.exists():
                    item = QtWidgets.QListWidgetItem(self._get_name(path))
                    item.setData(QtCore.Qt.UserRole, path)
                    item.setCheckState(QtCore.Qt.Checked)
                    self.list_selected.addItem(item)
        self.list_all.blockSignals(False)
        self.list_selected.blockSignals(False)

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
        self._save_selected_tools(self.combo_toolbar.currentData())

    def move_item(self, direction):
        row = self.list_selected.currentRow()
        if row < 0: return
        new_row = row + direction
        if 0 <= new_row < self.list_selected.count():
            item = self.list_selected.takeItem(row)
            self.list_selected.insertItem(new_row, item)
            self.list_selected.setCurrentRow(new_row)
            self.tools_changed.emit()

    # --- Utilitários ---
    def selected_tools(self):
        return [self.list_selected.item(i).data(QtCore.Qt.UserRole) for i in range(self.list_selected.count())]

    def _obter_nome_toolbar(self, path: Path) -> str:
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'Component'):
                return getattr(module.Component, 'toolbar_name', module.Component().windowTitle())
        except:
            pass
        return path.stem.replace("_", " ").title()

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