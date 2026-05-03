from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui


class FileExplorerTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.pasta_paciente = None
        self._init_ui()
        self._build_layout()

    def _init_ui(self):
        self.model = QtGui.QFileSystemModel()
        self.model.setReadOnly(False)

        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

        for i in range(1, 4):
            self.tree.hideColumn(i)

    def _build_layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tree)

    def set_data(self, data: dict, pasta: str = None):
        if pasta:
            self.pasta_paciente = pasta
            path = Path(pasta).absolute()
            self.model.setRootPath(str(path))
            self.tree.setRootIndex(self.model.index(str(path)))

    def _show_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return

        menu = QtWidgets.QMenu()
        abrir_pasta = menu.addAction("Abrir no Navegador")
        excluir = menu.addAction("Excluir")

        action = menu.exec_(self.tree.viewport().mapToGlobal(position))

        path_selecionado = self.model.filePath(index)

        if action == abrir_pasta:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path_selecionado))
        elif action == excluir:
            self._confirmar_exclusao(path_selecionado)

    def _confirmar_exclusao(self, path):
        res = QtWidgets.QMessageBox.question(
            self, "Confirmar", f"Deseja excluir permanentemente?\n{Path(path).name}"
        )
        if res == QtWidgets.QMessageBox.Yes:
            if Path(path).is_dir():
                shutil.rmtree(path)
            else:
                Path(path).unlink()


if __name__ == "__main__":
    import sys
    import shutil

    app = QtWidgets.QApplication(sys.argv)

    teste_dir = Path("pacients/Exploration_Test")
    teste_dir.mkdir(parents=True, exist_ok=True)
    (teste_dir / "projeto_01").mkdir(exist_ok=True)
    (teste_dir / "tomografia.dcm").write_text("dummy")

    window = FileExplorerTab()
    window.set_data({}, str(teste_dir.absolute()))
    window.resize(600, 400)
    window.show()

    sys.exit(app.exec())