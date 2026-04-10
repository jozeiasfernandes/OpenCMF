import sys
import json
import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from core.base import FluxoBase
from core.factory import ModuloFactory
from gui.home import PaginaHome
from gui.workspace import WorkspaceManager
from gui.editor_fluxo import PaginaEditorFluxo


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._configurar_janela()
        self._inicializar_ui()
        self._conectar_sinais()

    def _configurar_janela(self):
        self.setWindowTitle("OpenCMF - Modular Surgical Planning")
        self.setGeometry(150, 50, 1024, 650)

    def _inicializar_ui(self):
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = PaginaHome()
        self.editor_fluxo = PaginaEditorFluxo()
        self.workspace = WorkspaceManager()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.editor_fluxo)
        self.stack.addWidget(self.workspace)

    def _conectar_sinais(self):
        self.home.projeto_selecionado.connect(self.carregar_projeto)
        self.home.editor_solicitado.connect(
            lambda: self.stack.setCurrentWidget(self.editor_fluxo)
        )
        self.editor_fluxo.voltar_solicitado.connect(
            lambda: self.stack.setCurrentWidget(self.home)
        )
        self.workspace.home_solicitada.connect(self.navegar_home)

    def carregar_projeto(self, caminho_projeto):
        try:
            dados = self._ler_configuracao(caminho_projeto)
            self.workspace.clear()

            self.fluxo = FluxoBase(dados)
            for id_modulo in self.fluxo.sequencia:
                instancia = ModuloFactory.carregar_modulo(id_modulo)
                if instancia:
                    self.workspace.adicionar_modulo(id_modulo, instancia)

            self.stack.setCurrentWidget(self.workspace)

        except Exception as erro:
            logging.error(f"Erro ao carregar projeto: {erro}")
            QtWidgets.QMessageBox.critical(self, "Erro", f"Falha no projeto: {erro}")

    def navegar_home(self):
        self.stack.setCurrentWidget(self.home)

    def _ler_configuracao(self, caminho):
        with open(caminho, 'r', encoding="utf-8") as arquivo:
            return json.load(arquivo)


def carregar_estilo(app, caminho_qss):
    path = Path(caminho_qss)
    if path.exists():
        app.setStyleSheet(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    carregar_estilo(app, "temas/escuro.qss")

    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())