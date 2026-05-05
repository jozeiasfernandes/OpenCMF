import sys
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore


class Components_List(QtWidgets.QDialog):
    componente_alterado = QtCore.Signal(str, Path, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.workspace_dir = Path(__file__).resolve().parent
        self.components_path = self.workspace_dir.parent / "components"

        self.setWindowTitle("OpenCMF - Configuração de Componentes")
        self.resize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #d0d0d0; border-radius: 4px; }
            QTabBar::tab { padding: 10px 10px; }
        """)

        self.tabs.addTab(self._create_component_group("toolbars", multi=True), "Toolbars")
        self.tabs.addTab(self._create_component_group("toolboxes", multi=True), "Toolboxes")
        self.tabs.addTab(self._create_component_group("central_area", multi=False), "Central")

        main_layout.addWidget(self.tabs)

        btn_close = QtWidgets.QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        main_layout.addWidget(btn_close)

    def _create_component_group(self, subfolder, multi=True):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #d0d0d0; border-radius: 4px; }")

        content = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(content)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(8)

        files = self._get_py_files(subfolder)

        if not files:
            lbl = QtWidgets.QLabel("Nenhum componente encontrado")
            lbl.setStyleSheet("color: gray; font-style: italic;")
            vbox.addWidget(lbl)
        else:
            group = QtWidgets.QButtonGroup(widget) if not multi else None
            for file_path in files:
                name = file_path.stem.replace("_", " ").title()
                btn = QtWidgets.QCheckBox(name) if multi else QtWidgets.QRadioButton(name)

                if group:
                    group.addButton(btn)

                btn.toggled.connect(
                    lambda checked, f=file_path, s=subfolder:
                    self.componente_alterado.emit(s, f, checked)
                )
                vbox.addWidget(btn)

        vbox.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        return widget

    def _get_py_files(self, subfolder):
        folder_path = self.components_path / subfolder
        if folder_path.exists() and folder_path.is_dir():
            return sorted([
                f for f in folder_path.iterdir()
                if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"
            ])
        return []


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Components_List()
    window.componente_alterado.connect(lambda s, p, b: print(f"Tipo: {s} | Caminho: {p.name} | Ativo: {b}"))
    window.show()
    sys.exit(app.exec())