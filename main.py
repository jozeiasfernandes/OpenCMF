import sys
import json
import logging
import ctypes
from pathlib import Path
from typing import Dict, Any, List

from PySide6 import QtWidgets, QtCore, QtGui

from core.base import FluxoBase
from core.factory import ModuloFactory
from gui.tela_inicial import Tela_Inicial
from gui.workspace import WorkspaceManager
from gui.editor_fluxo import PaginaEditorFluxo
from gui.config import PaginaConfig

APP_ID = 'opencmf.surgicalplanning.1.0'
TITULO_APP = "OpenCMF - Modular Surgical Planning"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.pasta_paciente_atual = None
        self.modulos_instanciados: List[Any] = []

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
        self.config = PaginaConfig()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.editor_fluxo)
        self.stack.addWidget(self.workspace)
        self.stack.addWidget(self.config)

    def _carregar_icone(self):
        caminho_icone = Path(__file__).parent / "icones" / "cmf.png"
        if caminho_icone.exists():
            icone = QtGui.QIcon(str(caminho_icone))
            self.setWindowIcon(icone)
            QtWidgets.QApplication.setWindowIcon(icone)

    def _setup_connections(self):
        self.home.projeto_selecionado.connect(self.selecionar_paciente)
        self.home.fluxo_escolhido.connect(self.iniciar_fluxo_trabalho)
        self.home.editor_solicitado.connect(lambda: self.stack.setCurrentWidget(self.editor_fluxo))
        self.home.config_solicitada.connect(lambda: self.stack.setCurrentWidget(self.config))

        self.editor_fluxo.voltar_solicitado.connect(self.exibir_home)
        self.workspace.home_solicitada.connect(self.exibir_home)
        self.config.voltar_solicitado.connect(self.exibir_home)
        self.config.tema_alterado.connect(self.aplicar_tema)

        # Conecta a mudança de aba, mas note o tratamento no método abaixo
        self.workspace.currentChanged.connect(self._inicializar_modulo_ativo)

    def _log_debug(self, msg: str, dados: Any = None):
        print(f">>> [DEBUG SYSTEM] {msg}")
        if dados: print(f"    Conteúdo: {dados}")

    def exibir_home(self):
        self.home.atualizar_listas()
        self.stack.setCurrentWidget(self.home)

    def selecionar_paciente(self, caminho_pasta: str, modo: str):
        # Converte para caminho absoluto para evitar erros de referência no Windows
        caminho_abs = str(Path(caminho_pasta).resolve())
        self._log_debug("Paciente selecionado", caminho_abs)
        self.pasta_paciente_atual = caminho_abs

    def iniciar_fluxo_trabalho(self, caminho_json: str):
        self._log_debug("Iniciando fluxo", caminho_json)

        is_cadastro = "cadastro" in str(caminho_json).lower()
        if not is_cadastro and not self.pasta_paciente_atual:
            QtWidgets.QMessageBox.warning(self, "Atenção", "Selecione um paciente na lista.")
            return

        try:
            dados = json.loads(Path(caminho_json).read_text(encoding="utf-8"))
            self._configurar_workspace(dados)
            self.stack.setCurrentWidget(self.workspace)

            # A chamada inicial agora é segura
            self._inicializar_modulo_ativo()
        except Exception as e:
            self._notificar_erro("Falha ao carregar fluxo", e)

    def _configurar_workspace(self, dados: Dict[str, Any]):
        # Bloqueia sinais para que o currentChanged não dispare enquanto montamos o workspace
        self.workspace.blockSignals(True)

        self.workspace.clear()
        self.modulos_instanciados.clear()
        self.fluxo = FluxoBase(dados)

        for id_modulo in self.fluxo.sequencia:
            instancia = ModuloFactory.carregar_modulo(id_modulo)
            if instancia:
                instancia.concluido.connect(self._on_modulo_concluido)
                self.modulos_instanciados.append(instancia)
                self.workspace.adicionar_modulo(id_modulo, instancia)
                self._log_debug(f"Módulo '{id_modulo}' (ID: {hex(id(instancia))}) pronto.")

        self.workspace.blockSignals(False)

    def _inicializar_modulo_ativo(self):
        """
        MENSAGEM DE TESTE DE DEBUGGER:
        Iniciando processo de inicialização do módulo ativo.
        Verificando integridade da instância e bloqueando sinais recursivos.
        """
        modulo = self.workspace.get_modulo_ativo()
        if not modulo:
            return

        # PROTEÇÃO: Bloqueia sinais durante a inicialização para evitar loops infinitos de UI
        self.workspace.blockSignals(True)

        try:
            self._log_debug(f"Inicializando {type(modulo).__name__} em {hex(id(modulo))}")

            ws_widget = modulo.get_workspace()
            if ws_widget:
                ws_widget.updateGeometry()

            if self.pasta_paciente_atual:
                # Injeção de dados no módulo independente
                modulo.inicializar(self.pasta_paciente_atual)
                self._log_debug("Injeção de dados concluída.")
        finally:
            # Garante que os sinais sejam reativados mesmo se houver erro
            self.workspace.blockSignals(False)

    def _on_modulo_concluido(self):
        modulo_origem = self.sender()
        self._log_debug(f"Concluído: {type(modulo_origem).__name__}")

        if hasattr(modulo_origem, 'pasta_paciente') and modulo_origem.pasta_paciente:
            self.pasta_paciente_atual = str(Path(modulo_origem.pasta_paciente).resolve())

        if not self.workspace.avancar_aba():
            self.exibir_home()

    def aplicar_tema(self, caminho_qss: str):
        path = Path(caminho_qss)
        if path.exists():
            QtWidgets.QApplication.instance().setStyleSheet(path.read_text(encoding="utf-8"))

    def _notificar_erro(self, titulo: str, erro: Exception):
        logging.error(f"{titulo}: {erro}", exc_info=True)
        QtWidgets.QMessageBox.critical(self, "Erro", f"<b>{titulo}</b><br><br>{str(erro)}")


if __name__ == "__main__":
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    janela_principal = MainWindow()
    janela_principal.show()

    sys.exit(app.exec())