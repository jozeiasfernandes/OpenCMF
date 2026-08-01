import json
from pathlib import Path
from PySide6 import QtWidgets, QtGui


class TabKeyboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # parents[2] sobe de core/settings/tabs/general para core/settings
        base_path = Path(__file__).resolve().parents[2]
        self.config_path = base_path / "shortcut" / "shortcuts.json"

        self._setup_ui()
        self.carregar_atalhos()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Ação", "Descrição", "Atalho"])
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)

    def carregar_atalhos(self):
        if not self.config_path.exists():
            QtWidgets.QMessageBox.critical(self, "Erro", f"Arquivo não encontrado: {self.config_path}")
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.table.setRowCount(0)
        for action_id, info in data.items():
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(action_id))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(info.get("description", "")))

            editor = QtWidgets.QKeySequenceEdit()
            editor.setKeySequence(QtGui.QKeySequence(info.get("default", "")))
            editor.editingFinished.connect(
                lambda id=action_id, e=editor: self._salvar_atalho(id, e.keySequence().toString())
            )
            self.table.setCellWidget(row, 2, editor)

    def _salvar_atalho(self, action_id, shortcut_str):
        print(f"Atalho {action_id} alterado para {shortcut_str}")