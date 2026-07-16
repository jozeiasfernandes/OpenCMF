from typing import Dict, Any, Optional
from PySide6 import QtWidgets, QtCore
from core.workspace.contracts import IModule


class ModuloTemplate:
    def __init__(self):
        """Inicialização leve: apenas estados internos."""
        self.id = "template.modulo"
        self._is_initialized = False
        self.context: Dict[str, Any] = {}

        # UI components placeholders
        self._main_widget: Optional[QtWidgets.QWidget] = None

    def initialize(self, context: Dict[str, Any]) -> None:
        """
        Contrato: Injeção de dependências e configuração de estado.
        Substitui o antigo 'inicializar(caminho_paciente)'.
        """
        self.context = context
        self.pasta_paciente = context.get("caminho_paciente")

        # Extração de serviços injetados
        self.project_service = context.get("project_service")

        self._is_initialized = True
        print(f"Módulo {self.id} inicializado com sucesso.")

    def get_main_widget(self) -> QtWidgets.QWidget:
        """Contrato IModule: Retorna o widget central."""
        if not self._main_widget:
            self._main_widget = self._construir_ui()
        return self._main_widget

    def _construir_ui(self) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Área de conteúdo
        self.view_area = QtWidgets.QFrame()
        self.view_area.setStyleSheet("background-color: #1e1e1e;")
        layout.addWidget(self.view_area, stretch=1)

        return container

    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        toolbar = QtWidgets.QToolBar("Ferramentas")
        toolbar.addAction("Resetar Visão")
        return toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """Contrato IModule: Retorna dicionário de painéis laterais."""
        toolbox = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(toolbox)
        layout.addWidget(QtWidgets.QLabel("<b>PARÂMETROS</b>"))
        layout.addWidget(QtWidgets.QPushButton("Executar Cálculo"))
        return {"Parâmetros": toolbox}

    def cleanup(self) -> None:
        """Limpeza de recursos."""
        self._main_widget = None
        self._is_initialized = False