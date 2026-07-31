import logging
from typing import Optional, Any, Dict
from PySide6 import QtWidgets, QtCore
from modules.base_module.base_module import ModuloBase

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(ModuloBase):
    def __init__(self, context: Any = None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, parent=parent)

        self.id = "modulo.cefalometria"
        self.nome = "Cefalometria"

        # Criação dos componentes visuais do módulo
        self._main_widget: Optional[QtWidgets.QWidget] = None
        self._toolbox: Optional[QtWidgets.QWidget] = None

    def get_main_widget(self) -> QtWidgets.QWidget:
        """Retorna o widget principal do módulo (Área central)."""
        if not self._main_widget:
            self._main_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self._main_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            label = QtWidgets.QLabel("ÁREA DE TRAÇADO CEFALOMÉTRICO 2D/3D")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")

            layout.addWidget(label)

        return self._main_widget

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna um dicionário de painéis laterais (toolboxes)."""
        if not self._toolbox:
            self._toolbox = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self._toolbox)
            layout.setContentsMargins(0, 0, 0, 0)

            layout.addWidget(QtWidgets.QLabel("Pontos Anatômicos:"))
            layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Násio (N)"))
            layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Sela (S)"))
            layout.addStretch()

        return {"Ferramentas": self._toolbox}

    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        """Opcional: Retorna uma QToolBar se necessário."""
        return None

    def inicializar(self, caminho_paciente: str) -> None:
        """Inicializa o módulo com o caminho do paciente."""
        super().inicializar(caminho_paciente)
        logger.info(f"Módulo '{self.nome}' inicializado com paciente: {caminho_paciente}")

    def cleanup(self) -> None:
        """Limpeza segura de recursos e widgets."""
        try:
            if self._main_widget:
                if not hasattr(self._main_widget, "isVisible") or self._main_widget.isVisible() or self._main_widget:
                    try:
                        self._main_widget.deleteLater()
                    except RuntimeError:
                        pass
                self._main_widget = None

            if self._toolbox:
                try:
                    self._toolbox.deleteLater()
                except RuntimeError:
                    pass
                self._toolbox = None
        except Exception as e:
            logger.error(f"Erro ao limpar widgets do módulo {self.nome}: {e}")

        super().cleanup()
        logger.info(f"Módulo '{self.nome}' limpo com sucesso.")


if __name__ == "__main__":
    import sys

    # Criação da aplicação de teste isolado
    app = QtWidgets.QApplication(sys.argv)


    class MockContext:
        def __init__(self):
            self.app = app
            self.settings = {}


    # Instancia o módulo passando o contexto mock
    modulo = Modulo(context=MockContext())
    modulo.inicializar("./debug_paciente")

    # Janela de teste
    janela = QtWidgets.QMainWindow()
    janela.setWindowTitle("Teste do Módulo: Cefalometria")
    janela.resize(800, 600)

    central_widget = QtWidgets.QWidget()
    layout_principal = QtWidgets.QHBoxLayout(central_widget)

    toolboxes = modulo.get_toolboxes()
    main_widget = modulo.get_main_widget()

    layout_principal.addWidget(toolboxes["Ferramentas"], stretch=1)
    layout_principal.addWidget(main_widget, stretch=3)

    janela.setCentralWidget(central_widget)
    janela.show()

    sys.exit(app.exec())