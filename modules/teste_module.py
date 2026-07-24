import logging
from typing import Any, Dict, Optional
from PySide6 import QtWidgets

from core.workspace.workspace_manager import WorkspaceManager
from models.module_factory import ModuleFactory
from layout.layout import ModuleDistributor
from modules.base_module.base_module import ModuloBase

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(ModuloBase):
    """Módulo de teste para o sistema."""

    def __init__(self, context: Any, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, parent=parent)

        self.id = "modulo.teste"
        self.nome = "Módulo de Teste"

        self._main_widget: Optional[QtWidgets.QWidget] = None
        self._toolbox: Optional[QtWidgets.QWidget] = None
        self._toolbar: Optional[QtWidgets.QToolBar] = None

    def get_main_widget(self) -> Optional[QtWidgets.QWidget]:
        """Retorna o widget principal do módulo."""
        if not self._main_widget:
            self._main_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self._main_widget)

            # Widgets de exemplo
            label = QtWidgets.QLabel("Módulo de Teste Ativo")
            button = QtWidgets.QPushButton("Ação de Exemplo")

            layout.addWidget(label)
            layout.addWidget(button)
            layout.addStretch()

        return self._main_widget

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna os toolboxes do módulo."""
        if not self._toolbox:
            self._toolbox = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self._toolbox)

            btn1 = QtWidgets.QPushButton("Ferramenta 1")
            btn2 = QtWidgets.QPushButton("Ferramenta 2")

            layout.addWidget(btn1)
            layout.addWidget(btn2)
            layout.addStretch()

        return {"Operações": self._toolbox}

    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        """Retorna a toolbar do módulo."""
        if not self._toolbar:
            self._toolbar = QtWidgets.QToolBar("Toolbar do Módulo")
            self._toolbar.addAction("Nova Ação")
            self._toolbar.addAction("Salvar")
            self._toolbar.addSeparator()
            self._toolbar.addAction("Configurar")

        return self._toolbar

    def inicializar(self, caminho_paciente: str) -> None:
        """Inicializa o módulo com o caminho do paciente."""
        super().inicializar(caminho_paciente)
        logger.info(f"Módulo '{self.nome}' inicializado com paciente: {caminho_paciente}")

    def cleanup(self) -> None:
        """Limpa recursos do módulo."""
        # Limpa widgets
        if self._main_widget:
            self._main_widget.deleteLater()
            self._main_widget = None

        if self._toolbox:
            self._toolbox.deleteLater()
            self._toolbox = None

        if self._toolbar:
            self._toolbar.deleteLater()
            self._toolbar = None

        # Chama cleanup da base
        super().cleanup()

        logger.info(f"Módulo '{self.nome}' limpo")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("OpenCMF - Teste Módulo")


    # Contexto mock (em produção, seria o contexto real)
    class MockContext:
        def __init__(self):
            self.app = app
            self.settings = {}
            self.user_data = {}


    contexto_mock = MockContext()

    try:
        # Registra e cria o módulo via Factory
        ModuleFactory.register("modulo.teste", Modulo)
        ModuleFactory.set_context(contexto_mock)

        meu_modulo = ModuleFactory.create("modulo.teste")
        if not meu_modulo:
            raise RuntimeError("Falha ao criar módulo")

        # Cria e configura Workspace
        workspace = WorkspaceManager()

        # Inicializa módulo com caminho dummy
        meu_modulo.inicializar("./debug_paciente")

        # Distribui o módulo no workspace
        ModuleDistributor.distribute(
            meu_modulo,
            workspace.toolbar_manager,
            workspace.side_manager,
            workspace.central_manager
        )

        # Mostra workspace
        workspace.show()

        # Executa aplicação
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Erro durante execução: {e}", exc_info=True)
        sys.exit(1)