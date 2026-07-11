import logging
from typing import Dict
from PySide6 import QtWidgets, QtCore
from modules.base_module.base_module import ModuloBase


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Módulo teste"
        self.id = "modulo.modelo.vazio"

        self.main_container = QtWidgets.QWidget(self)
        self.layout_modulo = QtWidgets.QVBoxLayout(self)
        self.layout_modulo.setContentsMargins(0, 0, 0, 0)
        self.layout_modulo.addWidget(self.main_container)

        self._init_ui_components()

    def _init_ui_components(self):
        self.label_placeholder = QtWidgets.QLabel("Módulo em branco pronto para desenvolvimento.")
        self.label_placeholder.setAlignment(QtCore.Qt.AlignCenter)

        self.btn_exemplo = QtWidgets.QPushButton("Ação de Exemplo")

    def inicializar(self, caminho_projeto: str) -> None:
        super().inicializar(caminho_projeto)
        logging.info(f"Módulo {self.nome} inicializado em: {caminho_projeto}")

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.main_container.layout():
            return self.main_container

        layout = QtWidgets.QVBoxLayout(self.main_container)

        frame = QtWidgets.QFrame()
        lay_frame = QtWidgets.QVBoxLayout(frame)
        lay_frame.addWidget(self.label_placeholder)
        lay_frame.addWidget(self.btn_exemplo)
        lay_frame.addStretch()

        layout.addWidget(frame)
        return self.main_container

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        aba_ferramentas = QtWidgets.QWidget()
        lay_ferramentas = QtWidgets.QVBoxLayout(aba_ferramentas)

        lay_ferramentas.addWidget(QtWidgets.QPushButton("Ferramenta 1"))
        lay_ferramentas.addStretch()

        return {"Operações": aba_ferramentas}

    def cleanup(self) -> None:
        logging.info(f"Limpando recursos do módulo {self.id}")
        super().cleanup()