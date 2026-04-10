import sys
import json
import logging
import ctypes
from pathlib import Path
from typing import Dict, Any

from PySide6 import QtWidgets, QtCore, QtGui

from core.base import FluxoBase
from core.factory import ModuloFactory
from gui.tela_inicial import Tela_Inicial
from gui.workspace import WorkspaceManager
from gui.editor_fluxo import PaginaEditorFluxo

APP_ID = 'opencmf.surgicalplanning.version.1.0'
DIR_FLUXOS = Path("fluxos")
TITULO_APP = "OpenCMF - Modular Surgical Planning"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.pasta_paciente_atual = None

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        self.setWindowTitle(TITULO_APP)
        self.setGeometry(150, 50, 1024, 650)
        self._carregar_icone()

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = Tela_Inicial()
        self.editor_fluxo = PaginaEditorFluxo()
        self.workspace = WorkspaceManager()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.editor_fluxo)
        self.stack.addWidget(self.workspace)

    def _carregar_icone(self):
        caminho_icone = Path(__file__).parent / "icones" / "cmf.png"
        if caminho_icone.exists():
            icone = QtGui.QIcon(str(caminho_icone))
            self.setWindowIcon(icone)
            QtWidgets.QApplication.setWindowIcon(icone)

    def _setup_connections(self):
        self.home.fluxo_escolhido.connect(self.iniciar_novo_fluxo)
        self.home.projeto_selecionado.connect(self.abrir_projeto_existente)
        self.home.editor_solicitado.connect(self.exibir_editor)

        self.editor_fluxo.voltar_solicitado.connect(self.exibir_home)
        self.workspace.home_solicitada.connect(self.exibir_home)

    def exibir_home(self):
        self.home.atualizar_listas()
        self.stack.setCurrentWidget(self.home)

    def exibir_editor(self):
        self.stack.setCurrentWidget(self.editor_fluxo)

    def iniciar_novo_fluxo(self, caminho_json: str):
        try:
            config = self._carregar_configuracao(Path(caminho_json))
            self._configurar_fluxo_trabalho(config)
            self.stack.setCurrentWidget(self.workspace)
        except Exception as e:
            self._notificar_erro("Falha ao iniciar novo fluxo", e)

    def abrir_projeto_existente(self, caminho_pasta: str, modo: str):
        try:
            pasta_projeto = Path(caminho_pasta)
            config_projeto = self._carregar_configuracao(pasta_projeto / "projeto" / "info.json")

            nome_fluxo = config_projeto.get("fluxo_origem", "ortog.json")
            config_fluxo = self._carregar_configuracao(DIR_FLUXOS / nome_fluxo)

            self._configurar_fluxo_trabalho(config_fluxo)
            self.pasta_paciente_atual = str(pasta_projeto)

            self._inicializar_modulo_ativo()
            self.stack.setCurrentWidget(self.workspace)
        except Exception as e:
            self._notificar_erro("Não foi possível abrir o projeto", e)

    def _carregar_configuracao(self, caminho: Path) -> Dict[str, Any]:
        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        return json.loads(caminho.read_text(encoding="utf-8"))

    def _configurar_fluxo_trabalho(self, dados: Dict[str, Any]):
        self.workspace.clear()
        self.pasta_paciente_atual = None
        self.fluxo = FluxoBase(dados)

        for id_modulo in self.fluxo.sequencia:
            instancia = ModuloFactory.carregar_modulo(id_modulo)
            if instancia:
                instancia.concluido.connect(self._on_modulo_concluido)
                self.workspace.adicionar_modulo(id_modulo, instancia)

    def _on_modulo_concluido(self):
        modulo_emissor = self.sender()

        if getattr(modulo_emissor, 'pasta_paciente', None):
            self.pasta_paciente_atual = modulo_emissor.pasta_paciente
            logging.info(f"Contexto do paciente definido: {self.pasta_paciente_atual}")

        if self.workspace.avancar_aba() and self.pasta_paciente_atual:
            self._inicializar_modulo_ativo()

    def _inicializar_modulo_ativo(self):
        proximo_modulo = self.workspace.get_modulo_ativo()
        if proximo_modulo:
            proximo_modulo.inicializar(self.pasta_paciente_atual)

    def _notificar_erro(self, titulo: str, erro: Exception):
        logging.error(f"{titulo}: {erro}")
        QtWidgets.QMessageBox.critical(self, "Erro de Sistema", f"{titulo}\n\nDetalhes: {erro}")


def carregar_estilo_global(app: QtWidgets.QApplication, nome_arquivo: str):
    caminho = Path("temas") / nome_arquivo
    if caminho.exists():
        app.setStyleSheet(caminho.read_text(encoding="utf-8"))


if __name__ == "__main__":
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    carregar_estilo_global(app, "escuro.qss")

    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())