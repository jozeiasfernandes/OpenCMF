import sys
import logging
from core.workspace.workspace_manager import WorkspaceManager
from core.workspace.module_factory import ModuleFactory
from core.workspace.layout import ModuleDistributor

from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore
from core.workspace.contracts import IModule

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")

class Modulo(IModule):
    def __init__(self, **kwargs):
        super().__init__()
        # Inicialize apenas as instâncias aqui
        self._main_widget = None
        self._toolbox = None
        self._toolbar = None

    def get_main_widget(self) -> QtWidgets.QWidget:
        if not self._main_widget:
            self._main_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self._main_widget)
            layout.addWidget(QtWidgets.QLabel("Módulo de Teste Ativo"))
            layout.addWidget(QtWidgets.QPushButton("Ação de Exemplo"))
        return self._main_widget

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        if not self._toolbox:
            self._toolbox = QtWidgets.QWidget()
            lay = QtWidgets.QVBoxLayout(self._toolbox)
            lay.addWidget(QtWidgets.QPushButton("Ferramenta 1"))
            lay.addStretch()
        return {"Operações": self._toolbox}

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        if not self._toolbar:
            self._toolbar = QtWidgets.QToolBar("Toolbar do Módulo")
            self._toolbar.addAction("Nova Ação")
        return self._toolbar

    def cleanup(self) -> None:
        """
        O cleanup é chamado pelo WorkspaceRegistry/Distributor.
        Certifique-se de liberar referências pesadas aqui.
        """
        self._main_widget = None
        self._toolbox = None
        self._toolbar = None


if __name__ == "__main__":

    # 1. Inicia a aplicação Qt
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # 2. Registra e cria o módulo via Factory
    # Substitua "modulo.teste" pelo ID real que você definiu na sua arquitetura
    ModuleFactory.register("modulo.teste", Modulo)
    meu_modulo = ModuleFactory.create("modulo.teste")

    # 3. Inicializa o Workspace
    workspace = WorkspaceManager()

    # 4. Usa o ModuleDistributor para injetar os componentes
    # O Distributor lerá os métodos get_main_widget, get_toolboxes e get_workspace_toolbar
    # e fará a montagem automática no WorkspaceManager
    try:
        ModuleDistributor.distribute(
            meu_modulo,
            workspace.toolbar_manager,
            workspace.side_manager,
            workspace.central_host
        )
    except Exception as e:
        print(f"Erro ao distribuir o módulo: {e}")

    # 5. Exibe a interface
    workspace.resize(1024, 768)
    workspace.show()

    # 6. Loop principal
    sys.exit(app.exec())