import sys
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore


class OpenCMFWindow(QtWidgets.QWidget):
    def __init__(self, project_root):
        super().__init__()
        self.components_path = Path(project_root) / "core" / "components"
        self.setWindowTitle("OpenCMF - Componentes")
        self.resize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(self.create_checkbox_group("Toolbars", "toolbars"))
        layout.addWidget(self.create_checkbox_group("Toolboxes", "toolboxes"))
        layout.addWidget(self.create_radio_group("Área Central", "central_area"))

        layout.addStretch()

    def create_checkbox_group(self, title, subfolder):
        group = QtWidgets.QGroupBox(title)
        vbox = QtWidgets.QVBoxLayout(group)

        files = self.get_py_files(subfolder)
        if not files:
            vbox.addWidget(QtWidgets.QLabel("Nenhum componente"))
            return group

        for file in files:
            name = file.stem.replace("_", " ").title()
            cb = QtWidgets.QCheckBox(name)
            cb.toggled.connect(
                lambda checked, n=name, sf=subfolder:
                print(f"[CHECKBOX] {sf} -> {n}: {checked}")
            )
            vbox.addWidget(cb)

        return group

    def create_radio_group(self, title, subfolder):
        group = QtWidgets.QGroupBox(title)
        vbox = QtWidgets.QVBoxLayout(group)

        files = self.get_py_files(subfolder)
        if not files:
            vbox.addWidget(QtWidgets.QLabel("Nenhum componente"))
            return group

        btn_group = QtWidgets.QButtonGroup(group)
        btn_group.setExclusive(True)

        for file in files:
            name = file.stem.replace("_", " ").title()
            rb = QtWidgets.QRadioButton(name)

            rb.toggled.connect(
                lambda checked, n=name, sf=subfolder:
                checked and print(f"[RADIO] {sf} -> selecionado: {n}")
            )

            btn_group.addButton(rb)
            vbox.addWidget(rb)

        return group

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
        self.setWindowTitle("Teste OpenCMF")
        self.resize(500, 600)

        self.widget = OpenCMFWindow(project_root)
        self.setCentralWidget(self.widget)


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