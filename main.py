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
        # Lista para impedir que os módulos sejam deletados da memória pelo Python
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

    def _log_debug(self, msg: str, dados: Any = None):
        print(f">>> [DEBUG SYSTEM] {msg}")
        if dados: print(f"    Conteúdo: {dados}")

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

    def exibir_home(self):
        self.home.atualizar_listas()
        self.stack.setCurrentWidget(self.home)

    def selecionar_paciente(self, caminho_pasta: str, modo: str):
        self._log_debug("Paciente selecionado na lista", caminho_pasta)
        self.pasta_paciente_atual = caminho_pasta

    def iniciar_fluxo_trabalho(self, caminho_json: str):
        self._log_debug("Iniciando fluxo", caminho_json)
        # Permite avançar se for cadastro ou se já houver paciente selecionado
        if "cadastro" not in str(caminho_json).lower() and not self.pasta_paciente_atual:
            QtWidgets.QMessageBox.warning(self, "Atenção", "Selecione um paciente na lista antes de iniciar.")
            return

        try:
            dados = json.loads(Path(caminho_json).read_text(encoding="utf-8"))
            self._configurar_workspace(dados)
            self.stack.setCurrentWidget(self.workspace)
            self._inicializar_modulo_ativo()
        except Exception as e:
            self._notificar_erro("Falha ao carregar fluxo", e)

    def _configurar_workspace(self, dados: Dict[str, Any]):
        # Limpa o workspace e as referências antigas
        self.workspace.clear()
        self.modulos_instanciados.clear()

        self.fluxo = FluxoBase(dados)
        self._log_debug("Sequência", self.fluxo.sequencia)

        for id_modulo in self.fluxo.sequencia:
            instancia = ModuloFactory.carregar_modulo(id_modulo)
            if instancia:
                # Importante: conectar sinais ANTES de adicionar ao layout
                instancia.concluido.connect(self._on_modulo_concluido)

                # Guarda a referência física para o Garbage Collector não matar o objeto
                self.modulos_instanciados.append(instancia)

                # Adiciona à interface
                self.workspace.adicionar_modulo(id_modulo, instancia)
                self._log_debug(f"Conectado: {id_modulo}")

    def _inicializar_modulo_ativo(self):
        modulo = self.workspace.get_modulo_ativo()
        if modulo:
            self._log_debug(f"Inicializando: {type(modulo).__name__}")
            # Garante que o widget exista e força o layout a se atualizar
            ws = modulo.get_workspace()
            if ws:
                ws.updateGeometry()
                ws.repaint()
                self._log_debug("Workspace Widget: OK")

            # Chama a lógica de carregamento de dados do módulo
            modulo.inicializar(self.pasta_paciente_atual)
        else:
            self._log_debug("ERRO: Módulo ativo não encontrado")

    def _on_modulo_concluido(self):
        modulo_origem = self.sender()
        self._log_debug(f"Módulo {type(modulo_origem).__name__} concluído.")

        # Atualiza o paciente atual caso o módulo de cadastro tenha gerado um novo ID
        if hasattr(modulo_origem, 'pasta_paciente') and modulo_origem.pasta_paciente:
            self.pasta_paciente_atual = modulo_origem.pasta_paciente
            self._log_debug("Pasta do paciente atualizada", self.pasta_paciente_atual)

        if self.workspace.avancar_aba():
            self._inicializar_modulo_ativo()
        else:
            self._log_debug("Fim do fluxo. Retornando.")
            self.exibir_home()

    def aplicar_tema(self, caminho_qss: str):
        path = Path(caminho_qss)
        if path.exists():
            QtWidgets.QApplication.instance().setStyleSheet(path.read_text(encoding="utf-8"))

    def _notificar_erro(self, titulo: str, erro: Exception):
        logging.error(f"{titulo}: {erro}")
        QtWidgets.QMessageBox.critical(self, "Erro", f"{titulo}\n{erro}")


if __name__ == "__main__":
    # Garante que o ícone apareça na barra de tarefas do Windows
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Referência global da janela
    main_win = MainWindow()
    main_win.show()

    sys.exit(app.exec())