import sys
from pathlib import Path
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFrame,
    QVBoxLayout, QGridLayout, QApplication
)
from PySide6.QtCore import Qt, Signal, QPoint, QSize, QEvent
from PySide6.QtGui import QIcon
from core.localization.translator import get_base_dir, tr


def get_icon_path(icon_name: str) -> str:
    base_dir = get_base_dir()
    candidate = base_dir / "appearance" / "icons" / icon_name
    return str(candidate) if candidate.exists() else ""


class Card(QPushButton):
    def __init__(self, texto: str, cor: str, icone_nome: str, parent: Optional[QWidget] = None):
        super().__init__(texto, parent)
        self.setFixedSize(130, 40)
        self.setLayoutDirection(Qt.LeftToRight)

        icon_path = get_icon_path(icone_nome)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(30, 30))

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {cor};
                border-radius: 4px;
                color: black;
                font-weight: bold;
                border: none;
                font-size: 11px;
                text-align: left;
                padding-left: 10px;
            }}
            QPushButton:hover {{
                background-color: #ffffff;
            }}
        """)


class Secao(QFrame):
    def __init__(self, titulo: str, itens: list[tuple[str, str]], cor: str, callback: Callable[[str, str], None], parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignLeft)

        label = QLabel(titulo, self)
        label.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        layout.addWidget(label)

        grid = QGridLayout()
        grid.setAlignment(Qt.AlignLeft)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        colunas = 4
        for i, (nome, icone) in enumerate(itens):
            btn = Card(nome, cor, icone, self)
            btn.clicked.connect(lambda _, n=nome, t=titulo: callback(t, n))
            grid.addWidget(btn, i // colunas, i % colunas)

        layout.addLayout(grid)


class ImportObjectsPanel(QFrame):
    importRequested = Signal(str, str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setMinimumWidth(580)

        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self._setup_sections(layout)

    def _setup_sections(self, layout: QVBoxLayout) -> None:
        superficies = [
            (tr("import.superficies.cranio", "Crânio"), "cranio.svg"),
            (tr("import.superficies.maxila", "Maxila"), "maxilla.svg"),
            (tr("import.superficies.mandibula", "Mandíbula"), "mandible.svg"),
            (tr("import.superficies.pele", "Pele"), "face.svg"),
            (tr("import.superficies.outros", "Outros"), "stl.svg")
        ]
        layout.addWidget(Secao(tr("import.secao.superficies", "Superfícies"), superficies, "#b0a8c0", self._on_item_clicked, self))

        fotografias = [
            (tr("import.fotografias.frente", "Frente"), "fronte.svg"),
            (tr("import.fotografias.perfil", "Perfil"), "perfil.svg"),
            (tr("import.fotografias.intrabucal", "Intrabucal"), "photo.svg"),
            (tr("import.fotografias.outros", "Outros"), "photo.svg")
        ]
        layout.addWidget(Secao(tr("import.secao.fotografias", "Fotografias"), fotografias, "#c9a7a0", self._on_item_clicked, self))

        volumes = [(tr("import.volumes.volume_vti", "Volume .vti"), "vti.svg")]
        layout.addWidget(Secao(tr("import.secao.volume", "Volume"), volumes, "#bcd4d0", self._on_item_clicked, self))

    def _on_item_clicked(self, categoria: str, subcategoria: str) -> None:
        self.importRequested.emit(categoria, subcategoria)
        self.hide()

    def show_under(self, widget: QWidget) -> None:
        pos = widget.mapToGlobal(QPoint(0, widget.height() + 2))
        self.move(pos)
        self.show()
        self.setFocus()

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.WindowDeactivate:
            self.hide()
        return super().event(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_window = QWidget()
    test_window.setMinimumSize(800, 600)
    test_window.setStyleSheet("background-color: #1e1e1e;")

    btn = QPushButton(tr("import.btn.import_objects", "Import Objects"), test_window)
    btn.setFixedSize(130, 30)
    btn.move(50, 50)
    btn.setStyleSheet("background-color: #444; color: white;")

    panel = ImportObjectsPanel(test_window)
    btn.clicked.connect(lambda: panel.show_under(btn))
    panel.importRequested.connect(lambda cat, sub: print(f"Importando: {cat} -> {sub}"))

    test_window.show()
    sys.exit(app.exec())