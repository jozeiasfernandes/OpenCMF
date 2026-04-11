from PySide6 import QtWidgets, QtCore, QtGui
from typing import Dict, Any


class FluxoCard(QtWidgets.QFrame):
    clicado = QtCore.Signal(str)

    def __init__(self, dados: Dict[str, Any], caminho_fluxo: str, parent=None):
        super().__init__(parent)
        self.dados = dados
        self.caminho_fluxo = caminho_fluxo
        self.cor = dados.get("cor_fundo", {"r": 52, "g": 73, "b": 94})

        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("card_container")
        self.setCursor(QtCore.Qt.PointingHandCursor)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # 1. Bloco de Destaque (Título do Fluxo)
        self.bloco_titulo = self._criar_bloco_destaque(self.dados.get("nome", "Sem Nome"))
        layout.addWidget(self.bloco_titulo)

        # 2. Sequência de Módulos
        for modulo in self.dados.get("sequencia", []):
            widget_modulo = self._criar_bloco_modulo(modulo)
            layout.addWidget(widget_modulo)

        layout.addStretch()

    def _criar_bloco_destaque(self, texto: str) -> QtWidgets.QFrame:
        bloco = QtWidgets.QFrame()
        bloco.setFixedSize(180, 80)
        bloco.setStyleSheet(
            f"background-color: rgb({self.cor['r']}, {self.cor['g']}, {self.cor['b']}); "
            f"border-radius: 6px;"
        )

        lay = QtWidgets.QVBoxLayout(bloco)
        lbl = QtWidgets.QLabel(texto)
        lbl.setObjectName("label_fluxo")
        lbl.setWordWrap(True)
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setStyleSheet("color: white; font-weight: bold; border: none;")

        lay.addWidget(lbl)
        return bloco

    def _criar_bloco_modulo(self, texto: str) -> QtWidgets.QLabel:
        lbl = QtWidgets.QLabel(texto)
        lbl.setFixedSize(130, 80)
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setStyleSheet(
            f"background-color: rgba({self.cor['r']}, {self.cor['g']}, {self.cor['b']}, 150); "
            f"border-radius: 6px; color: white; border: 1px solid rgba(255,255,255,30);"
        )
        return lbl

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicado.emit(self.caminho_fluxo)
        super().mousePressEvent(event)