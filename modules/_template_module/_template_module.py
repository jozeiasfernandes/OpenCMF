from typing import Dict, Any, Optional
from PySide6 import QtWidgets


class Module:
    def __init__(self, **kwargs):
        self.id = "template.modulo"
        self._is_initialized = False

        # Armazena injeções úteis enviadas pelo factory
        self.context = kwargs

        # Extração opcional de dependências comuns
        self.scene_manager = kwargs.get("scene_manager")
        self.project_service = kwargs.get("project_service")

        # UI components placeholders
        self._central_area: Optional[QtWidgets.QWidget] = None

    def initialize(self, context: Dict[str, Any]) -> None:
        """
        Contrato: Injeção de dependências e configuração de estado.
        """
        self.context = context
        self.pasta_paciente = context.get("path_pacient")

        # Extração de serviços injetados
        self.project_service = context.get("project_service")

        self._is_initialized = True
        print(f"Módulo {self.id} inicializado com sucesso.")

    def get_central_area(self) -> QtWidgets.QWidget:
        """Retorna o widget principal da área central do módulo."""
        if not self._central_area:
            self._central_area = QtWidgets.QLabel("Módulo Template Carregado")
        return self._central_area

    def _construir_ui(self) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Área de conteúdo
        self.view_area = QtWidgets.QFrame()
        self.view_area.setStyleSheet("background-colors: #1e1e1e;")
        layout.addWidget(self.view_area, stretch=1)

        return container

    def get_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        """Retorna a barra de ferramentas do módulo."""
        toolbar = QtWidgets.QToolBar("Ferramentas")
        toolbar.addAction("Resetar Visão")
        return toolbar

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        """Contrato IModule: Retorna dicionário de painéis laterais."""
        side_panel_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(side_panel_widget)
        layout.addWidget(QtWidgets.QLabel("<b>PARÂMETROS</b>"))
        layout.addWidget(QtWidgets.QPushButton("Executar Cálculo"))
        return {"Parâmetros": side_panel_widget}

    def cleanup(self) -> None:
        """Limpeza de recursos."""
        self._central_area = None
        self._is_initialized = False


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    modulo = ModuloTemplate()

    contexto_teste = {
        "path_pacient": "C:/Dados/Paciente_Teste_01",
        "project_service": None
    }
    modulo.initialize(contexto_teste)
    janela = QtWidgets.QMainWindow()
    janela.setWindowTitle(f"Teste de Interface: {modulo.id}")
    janela.resize(1024, 768)
    central = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(central)

    side_panels = modulo.get_side_panel()
    if side_panels:
        primeira_chave = list(side_panels.keys())[0]
        layout.addWidget(side_panels[primeira_chave], stretch=1)
    layout.addWidget(modulo.get_central_area(), stretch=3)
    janela.setCentralWidget(central)
    janela.show()
    sys.exit(app.exec())