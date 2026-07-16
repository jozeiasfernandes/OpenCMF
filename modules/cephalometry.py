import logging
from PySide6 import QtWidgets, QtCore
from modules.base_module.base_module import ModuloBase
from core.workspace.contracts import IModule

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")

class Modulo(ModuloBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = "modulo.cefalometria"

    def get_main_widget(self) -> QtWidgets.QWidget:
        """Substitui o antigo get_workspace."""
        label = QtWidgets.QLabel("ÁREA DE TRAÇADO CEFALOMÉTRICO 2D/3D")
        label.setAlignment(QtCore.Qt.AlignCenter)
        return label

    def get_toolboxes(self) -> dict[str, QtWidgets.QWidget]:
        """Substitui o antigo get_toolbox retornando um dicionário de painéis."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QtWidgets.QLabel("Pontos Anatômicos:"))
        layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Násio (N)"))
        layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Sela (S)"))
        layout.addStretch()

        return {"Ferramentas": widget}

    def get_workspace_toolbar(self) -> None:
        """Opcional: Retorna uma QToolBar se necessário."""
        return None

    def cleanup(self) -> None:
        """Limpeza de recursos."""
        logger.info("Limpeza do módulo de Cefalometria realizada.")


if __name__ == "__main__":
    import sys

    # Criação da aplicação
    app = QtWidgets.QApplication(sys.argv)

    # Instancia o seu módulo
    modulo = Modulo()

    # Cria uma janela principal para envolver o módulo
    janela = QtWidgets.QMainWindow()
    janela.setWindowTitle("Teste do Módulo: Cefalometria")
    janela.resize(800, 600)

    # Configura o layout da janela
    central_widget = QtWidgets.QWidget()
    layout_principal = QtWidgets.QHBoxLayout(central_widget)

    # Acessa os novos métodos do protocolo IModule
    toolboxes = modulo.get_toolboxes()
    main_widget = modulo.get_main_widget()

    # Adiciona a toolbox ("Ferramentas") e o widget principal
    # Usamos o dicionário retornado pelo get_toolboxes
    layout_principal.addWidget(toolboxes["Ferramentas"], stretch=1)
    layout_principal.addWidget(main_widget, stretch=3)

    janela.setCentralWidget(central_widget)

    # Exibe a janela
    janela.show()

    # Executa o loop de eventos
    sys.exit(app.exec())