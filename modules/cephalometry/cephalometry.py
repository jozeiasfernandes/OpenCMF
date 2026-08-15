import logging
from typing import Optional, Any, Dict
from PySide6 import QtWidgets, QtCore


# Workspace
from core.workspace.modules.base.base_module import ModuleBase

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(ModuleBase):
    def __init__(self, context: Any = None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, parent=parent)

        self.id = "modulo.cefalometria"
        self.nome = "Cefalometria"

        # Criação dos componentes visuais do módulo
        self._main_widget: Optional[QtWidgets.QWidget] = None
        self._side_panel_widget: Optional[QtWidgets.QWidget] = None
        self._toolbar: Optional[QtWidgets.QToolBar] = None

    def get_central_area(self) -> QtWidgets.QWidget:
        """Retorna o widget principal do módulo (Área central)."""
        if not self._main_widget:
            self._main_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self._main_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            label = QtWidgets.QLabel("ÁREA DE TRAÇADO CEFALOMÉTRICO 2D/3D")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px; font-weight: bold; colors: #fff;")

            layout.addWidget(label)

        return self._main_widget

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna um dicionário de painéis laterais (side_panel)."""
        if not self._side_panel_widget:
            self._side_panel_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self._side_panel_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            layout.addWidget(QtWidgets.QLabel("Pontos Anatômicos:"))
            layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Násio (N)"))
            layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Sela (S)"))
            layout.addStretch()

        return {"Ferramentas": self._side_panel_widget}

    def get_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        """Retorna a QToolBar do módulo para testes e uso no workspace."""
        if not self._toolbar:
            self._toolbar = QtWidgets.QToolBar("Ferramentas Cefalometria")
            self._toolbar.addAction("Zoom In")
            self._toolbar.addAction("Zoom Out")
            self._toolbar.addSeparator()
            self._toolbar.addAction("Resetar Visão")
        return self._toolbar

    def inicializar(self, path_pacient: str) -> None:
        """Inicializa o módulo com o path do paciente."""
        super().inicializar(path_pacient)
        logger.info(f"Módulo '{self.nome}' inicializado com paciente: {path_pacient}")

    def cleanup(self) -> None:
        """Limpeza segura de recursos e widgets."""
        try:
            if self._main_widget:
                try:
                    self._main_widget.deleteLater()
                except RuntimeError:
                    pass
                self._main_widget = None

            if self._side_panel_widget:
                try:
                    self._side_panel_widget.deleteLater()
                except RuntimeError:
                    pass
                self._side_panel_widget = None

            if self._toolbar:
                try:
                    self._toolbar.deleteLater()
                except RuntimeError:
                    pass
                self._toolbar = None
        except Exception as e:
            logger.error(f"Erro ao limpar widgets do módulo {self.nome}: {e}")

        super().cleanup()
        logger.info(f"Módulo '{self.nome}' limpo com sucesso.")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    class MockContext:
        def __init__(self):
            self.app = app
            self.settings = {}

    modulo = Modulo(context=MockContext())
    modulo.inicializar("./debug_paciente")

    janela = QtWidgets.QMainWindow()
    janela.setWindowTitle("Teste do Módulo: Cefalometria")
    janela.resize(1024, 768)

    # Adicionando a Toolbar na janela principal de teste
    toolbar = modulo.get_toolbar()
    if toolbar:
        janela.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)

    # Organizando o layout na ordem correta: Área Central à esquerda (maior espaço) e Side Panel à direita
    central_widget = QtWidgets.QWidget()
    layout_principal = QtWidgets.QHBoxLayout(central_widget)
    layout_principal.setContentsMargins(0, 0, 0, 0)

    side_panels = modulo.get_side_panel()
    main_widget = modulo.get_central_area()

    # 1. Área central primeiro (fica à esquerda no layout horizontal)
    layout_principal.addWidget(main_widget, stretch=3)

    # 2. Side panel depois (fica à direita)
    if side_panels:
        primeira_chave = list(side_panels.keys())[0]
        layout_principal.addWidget(side_panels[primeira_chave], stretch=1)

    janela.setCentralWidget(central_widget)
    janela.show()

    sys.exit(app.exec())