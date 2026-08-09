from PySide6 import QtWidgets, QtCore
from typing import Dict, Any


class FluxoCard(QtWidgets.QFrame):
    clicado = QtCore.Signal(str)

    def __init__(self, dados: Dict[str, Any], caminho_fluxo: str, parent=None):
        super().__init__(parent)
        self.dados = dados
        self.caminho_fluxo = caminho_fluxo

        self._cards()

    def _cards(self):
        self.setObjectName("FluxoCard")
        self.setCursor(QtCore.Qt.PointingHandCursor)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # 1. Bloco de Destaque (Título do Fluxo)
        self.bloco_titulo = self._retang_fluxo(self.dados.get("nome", "Sem Nome"))
        layout.addWidget(self.bloco_titulo)

        # 2. Sequência de Módulos
        for i, modulo in enumerate(self.dados.get("sequencia", [])):
            if i > 0:
                seta = QtWidgets.QLabel("➔")
                seta.setObjectName("FluxoCardArrow")
                layout.addWidget(seta)

            widget_modulo = self._retang_modulo(modulo)
            layout.addWidget(widget_modulo)

        layout.addStretch()

    def _retang_fluxo(self, texto: str) -> QtWidgets.QFrame:
        bloco = QtWidgets.QFrame()
        bloco.setObjectName("FluxoCardMainBlock")
        bloco.setFixedSize(200, 80)

        lay = QtWidgets.QVBoxLayout(bloco)
        lbl = QtWidgets.QLabel(texto)
        lbl.setObjectName("FluxoCardTitleLabel")
        lbl.setWordWrap(True)
        lbl.setAlignment(QtCore.Qt.AlignCenter)

        lay.addWidget(lbl)
        return bloco

    def _retang_modulo(self, texto: str) -> QtWidgets.QLabel:
        lbl = QtWidgets.QLabel(texto)
        lbl.setObjectName("FluxoCardModuleLabel")
        lbl.setFixedSize(140, 70)
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        return lbl

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicado.emit(self.caminho_fluxo)
        super().mousePressEvent(event)