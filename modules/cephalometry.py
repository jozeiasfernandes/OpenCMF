from modules.base_module.base_module import ModuloBase
from PySide6 import QtWidgets, QtCore


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()

    def verificar_pre_requisitos(self) -> tuple[bool, str]:
        # Exemplo: Simula que a Tomografia já foi carregada
        return True, ""

    def get_workspace(self) -> QtWidgets.QWidget:
        # Área central representando o traçado cefalométrico
        label = QtWidgets.QLabel("ÁREA DE TRAÇADO CEFALOMÉTRICO 2D/3D")
        label.setAlignment(QtCore.Qt.AlignCenter)
        return label

    def get_toolbox(self) -> QtWidgets.QWidget:
        # Ferramentas específicas para marcação de pontos
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        layout.addWidget(QtWidgets.QLabel("Pontos Anatômicos:"))
        layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Násio (N)"))
        layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Sela (S)"))
        layout.addStretch()  # Empurra os botões para cima

        return widget