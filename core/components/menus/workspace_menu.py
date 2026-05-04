import sys
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore


class OpenCMFContextMenu(QtWidgets.QMenu):
    def __init__(self, project_root, parent=None):
        super().__init__("OpenCMF Menu", parent)
        self.components_path = Path(project_root) / "core" / "components"
        self.setup_menu()

    def setup_menu(self):
        toolbar_menu = self.addMenu("Toolbars")
        self.add_checkbox_entries(toolbar_menu, "toolbars")

        toolbox_menu = self.addMenu("Toolboxes")
        self.add_checkbox_entries(toolbox_menu, "toolboxes")

        central_menu = self.addMenu("Area Central")
        self.add_radio_entries(central_menu, "central_area")

    def add_checkbox_entries(self, menu, subfolder):
        files = self.get_py_files(subfolder)
        if not files:
            menu.addAction("Nenhum componente").setEnabled(False)
            return

        for file in files:
            display_name = file.stem.replace("_", " ").title()
            action = menu.addAction(display_name)
            action.setCheckable(True)
            action.toggled.connect(
                lambda checked, name=display_name, sf=subfolder:
                print(f"[CHECKBOX] {sf} -> {name}: {checked}")
            )

    def add_radio_entries(self, menu, subfolder):
        files = self.get_py_files(subfolder)
        if not files:
            menu.addAction("Nenhum componente").setEnabled(False)
            return

        group = QtGui.QActionGroup(menu)
        group.setExclusive(True)

        for file in files:
            display_name = file.stem.replace("_", " ").title()
            action = menu.addAction(display_name)
            action.setCheckable(True)
            action.setActionGroup(group)
            action.triggered.connect(
                lambda checked, name=display_name, sf=subfolder:
                print(f"[RADIO] {sf} -> selecionado: {name}")
            )

    def get_py_files(self, subfolder):
        folder_path = self.components_path / subfolder
        if folder_path.exists() and folder_path.is_dir():
            return [
                f for f in folder_path.iterdir()
                if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"
            ]
        return []


class TestWindow(QtWidgets.QMainWindow):
    def __init__(self, project_root):
        super().__init__()
        self.project_root = project_root
        self.setWindowTitle("Menu de Contexto OpenCMF")
        self.resize(400, 300)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        menu = OpenCMFContextMenu(self.project_root, self)
        menu.exec(self.mapToGlobal(pos))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    base_dir = "C:/OpenCMF"
    if not Path(base_dir).exists():
        base_dir = (
            Path(__file__).parent.parent
            if "core" not in str(Path(__file__).parent)
            else Path(__file__).parent.parent.parent
        )

    window = TestWindow(base_dir)
    window.show()
    sys.exit(app.exec())