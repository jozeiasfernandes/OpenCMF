from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional
from functools import partial

from PySide6 import QtWidgets, QtGui, QtCore

# Tabs
from components_loaders.tools_tab_loaders.tools_tab_loaders import ToolsTab


class ComponentCard(QtWidgets.QFrame):
    toggled = QtCore.Signal(bool)

    def __init__(self, name: str, file_path: Path, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.thumb_path = file_path.with_suffix(".png")
        self._setup_ui(name)

    # =========================================================================
    # UI SETUP & LAYOUT
    # =========================================================================
    def _setup_ui(self, name: str) -> None:
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

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

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.components_path = self.root_dir / "core" / "components"

        self.setWindowTitle("OpenCMF - Componentes")
        self.resize(900, 600)
        self.setup_ui()

    # =========================================================================
    # UI SETUP & TABS
    # =========================================================================
    def setup_ui(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabs.setStyleSheet("QTabBar::tab { height: 80px; width: 40px; }")

        def get_name(item: Any) -> str:
            if isinstance(item, dict):
                return item.get("display_name", "Desconhecido")
            return item.stem.replace("_", " ").title()

        self.tools_tab = ToolsTab(self.components_path, get_name)

        self.tabs.addTab(self.tools_tab, "Tools")
        self.tabs.addTab(self._create_group("toolbars", mode="card"), "Toolbars")
        self.tabs.addTab(self._create_group("side_panel", mode="check"), "Side Panel")
        self.tabs.addTab(self._create_group("central_area", mode="radio"), "Central")

        main_layout.addWidget(self.tabs)

        self.btn_confirmar = QtWidgets.QPushButton("Fechar")
        self.btn_confirmar.setFixedHeight(36)
        self.btn_confirmar.clicked.connect(self.accept)

        footer = QtWidgets.QVBoxLayout()
        footer.setContentsMargins(10, 10, 10, 10)
        footer.addWidget(self.btn_confirmar)
        main_layout.addLayout(footer)

    def _create_group(self, folder_name: str, mode: str) -> QtWidgets.QScrollArea:
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        content = QtWidgets.QWidget()
        content.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        layout = QtWidgets.QVBoxLayout(content)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        files = self._get_files_recursively(self.components_path / folder_name)
        group = QtWidgets.QButtonGroup(content) if mode == "radio" else None

        for path in files:
            display_name = self._get_component_name(path)

            if mode == "card":
                widget = ComponentCard(display_name, path)
                selector = widget.selector
            else:
                if mode == "check":
                    selector = QtWidgets.QCheckBox(display_name)
                else:
                    selector = QtWidgets.QRadioButton(display_name)
                selector.setStyleSheet("font-size: 12px; padding: 4px;")
                widget = selector

            if group:
                group.addButton(selector)

            selector.toggled.connect(
                partial(self._issue_change, folder_name, path)
            )

            layout.addWidget(widget)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    # =========================================================================
    # PRIVATE HELPERS & SLOTS
    # =========================================================================
    def _issue_change(self, folder: str, path: Path, checked: bool) -> None:
        self.componente_alterado.emit(folder, path, checked)

    def _get_files_recursively(self, directory: Path) -> list[Path]:
        if not directory.exists():
            return []
        return sorted([f for f in directory.glob("*.py") if f.name != "__init__.py"])

    def _get_component_name(self, caminho_arquivo: Path) -> str:
        try:
            import importlib.util
            import inspect
            from core.components.bases.base_central_area import CentralAreaBase

            spec = importlib.util.spec_from_file_location(caminho_arquivo.stem, caminho_arquivo)
            if spec and spec.loader:
                modulo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo)

                for name, obj in inspect.getmembers(modulo, inspect.isclass):
                    if issubclass(obj, CentralAreaBase) and obj is not CentralAreaBase:
                        return getattr(obj, 'side_panel_name', caminho_arquivo.stem.replace("_", " ").title())

        except Exception as e:
            print(f"Erro ao ler metadados de {caminho_arquivo.name}: {e}")

        return caminho_arquivo.stem.replace("_", " ").title()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Components_List()
    window.componente_alterado.connect(
        lambda s, p, b: print(f"{s} | {p.name} | {b}")
    )
    window.show()
    sys.exit(app.exec())