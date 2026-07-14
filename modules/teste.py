from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore
from core.workspace.contracts import IModule

class Modulo:
    # Garante que a classe respeita o protocolo IModule (opcional, mas recomendado)
    def __init__(self):
        self.nome = "Módulo de Teste"

    def get_main_widget(self) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        label = QtWidgets.QLabel("Módulo em branco pronto para desenvolvimento.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QPushButton("Ação de Exemplo"))
        return container

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        aba_ferramentas = QtWidgets.QWidget()
        lay_ferramentas = QtWidgets.QVBoxLayout(aba_ferramentas)
        lay_ferramentas.addWidget(QtWidgets.QPushButton("Ferramenta 1"))
        lay_ferramentas.addStretch()
        return {"Operações": aba_ferramentas}

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        """Implementação necessária para suporte a toolbars no workspace."""
        toolbar = QtWidgets.QToolBar("Toolbar do Módulo")
        toolbar.addAction("Nova Ação")
        return toolbar

    def cleanup(self) -> None:
        """Limpeza necessária para evitar memory leaks ao trocar de módulo."""
        pass