import sys
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore


class ComponentCard(QtWidgets.QFrame):
    toggled = QtCore.Signal(bool)

    def __init__(self, name: str, file_path: Path):
        super().__init__()
        self.thumb_path = file_path.with_suffix(".png")
        self._setup_ui(name)

    def _setup_ui(self, name):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setStyleSheet("""
            ComponentCard { 
                background-color: transparent; 
                border-radius: 4px; 
                border: 1px solid #D0D0D0; 
            }
            ComponentCard:hover { border: 1px solid #A0A0A0; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        header = QtWidgets.QHBoxLayout()
        self.selector = QtWidgets.QCheckBox()
        self.selector.setFixedSize(20, 18)

        title = QtWidgets.QLabel(name)
        title.setStyleSheet("font-size: 11px")

        header.addWidget(self.selector)
        header.addWidget(title)
        header.addStretch()

        self.preview = QtWidgets.QLabel()
        self.preview.setFixedHeight(32)
        self.preview.setStyleSheet("background-color: #8c8c8c; border-radius: 2px;")

        if self.thumb_path.exists():
            pix = QtGui.QPixmap(str(self.thumb_path))
            self.preview.setPixmap(pix.scaled(
                800, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            ))

        layout.addLayout(header)
        layout.addWidget(self.preview)
        self.selector.toggled.connect(self.toggled.emit)


class Components_List(QtWidgets.QDialog):
    componente_alterado = QtCore.Signal(str, Path, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.workspace_dir = Path(__file__).resolve().parent
        self.components_path = self.workspace_dir.parent / "components"
        self.setWindowTitle("OpenCMF - Componentes")
        self.resize(500, 600)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabs.setStyleSheet("QTabBar::tab { height: 80px; width: 40px; }")

        self.tabs.addTab(self._create_group("toolbars", mode="card"), "Toolbars")
        self.tabs.addTab(self._create_group("toolboxes", mode="check"), "Toolboxes")
        self.tabs.addTab(self._create_group("central_area", mode="radio"), "Central")

        main_layout.addWidget(self.tabs)

        self.btn_confirmar = QtWidgets.QPushButton("Confirmar")
        self.btn_confirmar.setFixedHeight(36)
        self.btn_confirmar.clicked.connect(self.accept)

        footer = QtWidgets.QVBoxLayout()
        footer.setContentsMargins(10, 10, 10, 10)
        footer.addWidget(self.btn_confirmar)
        main_layout.addLayout(footer)

    def _create_group(self, folder_name, mode):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        files = self._get_py_files(folder_name)
        group = QtWidgets.QButtonGroup(content) if mode == "radio" else None

        for path in files:
            display_name = self._obter_nome_componente(path)
            if mode == "card":
                widget = ComponentCard(display_name, path)
                selector = widget.selector
            else:
                selector = QtWidgets.QCheckBox(display_name) if mode == "check" else QtWidgets.QRadioButton(display_name)
                selector.setStyleSheet("font-size: 12px; padding: 4px;")
                widget = selector

            if group:
                group.addButton(selector)

            selector.toggled.connect(
                lambda checked, f=path, s=folder_name: self.componente_alterado.emit(s, f, checked)
            )
            layout.addWidget(widget)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _get_py_files(self, subfolder):
        path = self.components_path / subfolder
        if not path.exists(): return []
        return sorted([f for f in path.iterdir() if f.suffix == ".py" and f.name != "__init__.py"])

    def _obter_nome_componente(self, caminho_arquivo: Path) -> str:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(caminho_arquivo.stem, caminho_arquivo)
            if spec and spec.loader:
                modulo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo)

                if hasattr(modulo, 'Component') and hasattr(modulo.Component, 'toolbox_name'):
                    return modulo.Component.toolbox_name
        except Exception:
            pass

        return caminho_arquivo.stem.replace("_", " ").title()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Components_List()
    window.componente_alterado.connect(lambda s, p, b: print(f"{s} | {p.name} | {b}"))
    window.show()
    sys.exit(app.exec())