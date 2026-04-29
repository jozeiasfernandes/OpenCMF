import os
import sys
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFrame,
    QVBoxLayout, QGridLayout, QApplication
)
from PySide6.QtCore import Qt, Signal, QPoint, QSize
from PySide6.QtGui import QIcon


class Card(QPushButton):
    def __init__(self, texto, cor, icone_nome):
        super().__init__(texto)
        self.setFixedSize(130, 40)
        self.setLayoutDirection(Qt.LeftToRight)

        dir_atual = os.path.dirname(os.path.abspath(__file__))

        # Subindo 2 níveis: de 'core/imports' para a raiz 'OpenCMF'
        icon_path = os.path.abspath(os.path.join(dir_atual, "..", "..", "appearance", "icons", icone_nome))

        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))

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
    def __init__(self, titulo, itens_com_icones, cor, callback):
        super().__init__()
        self.setStyleSheet("QFrame { border: none; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignLeft)

        label = QLabel(titulo)
        label.setStyleSheet("color: white; font-size: 13px; font-weight: bold; margin-bottom: 2px;")
        layout.addWidget(label)

        grid = QGridLayout()
        grid.setAlignment(Qt.AlignLeft)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        colunas = 4
        for i, (nome, icone) in enumerate(itens_com_icones):
            btn = Card(nome, cor, icone)
            btn.clicked.connect(lambda _, n=nome: callback(n))
            grid.addWidget(btn, i // colunas, i % colunas)

        layout.addLayout(grid)


class ImportObjectsPanel(QFrame):
    importRequested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedWidth(580)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #666;
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        superficies = [
            ("Crânio", "cranio.svg"), ("Maxila", "stl.png"),
            ("Mandíbula", "stl.png"), ("Pele", "stl.png"), ("Outros", "stl.png")
        ]
        layout.addWidget(Secao("Superfícies", superficies, "#b0a8c0", self._on_item_clicked))

        fotos = [
            ("Frente", "photo.png"), ("Perfil", "photo.png"),
            ("Intrabucal", "photo.png"), ("Outros", "photo.png")
        ]
        layout.addWidget(Secao("Fotografias", fotos, "#c9a7a0", self._on_item_clicked))

        volumes = [("Volume .vti", "vti.png")]
        layout.addWidget(Secao("Volume", volumes, "#bcd4d0", self._on_item_clicked))

    def _on_item_clicked(self, nome):
        self.importRequested.emit(nome)
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_window = QWidget()
    test_window.setMinimumSize(800, 600)
    test_window.setStyleSheet("background-color: #1e1e1e;")
    btn_abrir = QPushButton("Import Objects", test_window)
    btn_abrir.setFixedSize(130, 30)
    btn_abrir.move(50, 50)
    btn_abrir.setStyleSheet("background-color: #444; color: white; border: 1px solid #666;")
    panel = ImportObjectsPanel(test_window)


    def toggle_panel():
        pos = btn_abrir.mapToGlobal(QPoint(0, btn_abrir.height() + 2))
        panel.move(pos)
        panel.show()


    btn_abrir.clicked.connect(toggle_panel)
    test_window.show()
    sys.exit(app.exec())