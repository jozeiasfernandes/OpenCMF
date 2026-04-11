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
from gui.config import PaginaConfig

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

        # Inicialização das Páginas
        self.home = Tela_Inicial()
        self.editor_fluxo = PaginaEditorFluxo()
        self.workspace = WorkspaceManager()
        self.config = PaginaConfig()

        # Adição ao Stack
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.editor_fluxo)
        self.stack.addWidget(self.workspace)
        self.stack.addWidget(self.config)

    def _carregar_icone(self):
        """Carrega o ícone principal do sistema."""
        caminho_icone = Path(__file__).parent / "icones" / "cmf.png"
        if caminho_icone.exists():
            icone = QtGui.QIcon(str(caminho_icone))
            self.setWindowIcon(icone)
            QtWidgets.QApplication.setWindowIcon(icone)

    def _setup_connections(self):
        """Conecta os sinais das páginas à lógica da MainWindow."""
        # Sinais da Home
        self.home.fluxo_escolhido.connect(self.iniciar_novo_fluxo)
        self.home.projeto_selecionado.connect(self.abrir_projeto_existente)
        self.home.editor_solicitado.connect(self.exibir_editor)
        self.home.config_solicitada.connect(self.exibir_config)

        # Sinais de Navegação (Voltar)
        self.editor_fluxo.voltar_solicitado.connect(self.exibir_home)
        self.workspace.home_solicitada.connect(self.exibir_home)
        self.config.voltar_solicitado.connect(self.exibir_home)

        # Sinais de Configuração
        self.config.tema_alterado.connect(self.aplicar_tema)
        self.config.idioma_alterado.connect(self.aplicar_idioma)

    # --- Navegação ---

    def exibir_home(self):
        self.home.atualizar_listas()
        self.stack.setCurrentWidget(self.home)

    def exibir_editor(self):
        self.stack.setCurrentWidget(self.editor_fluxo)

    def exibir_config(self):
        self.stack.setCurrentWidget(self.config)

    # --- Lógica de Estilo e Sistema ---

    def aplicar_tema(self, caminho_qss: str):
        """Aplica o arquivo de folha de estilo globalmente."""
        if not caminho_qss: return

        path = Path(caminho_qss)
        if path.exists():
            try:
                css = path.read_text(encoding="utf-8")
                QtWidgets.QApplication.instance().setStyleSheet(css)
                logging.info(f"Tema aplicado: {path.name}")
            except Exception as e:
                logging.error(f"Erro ao carregar QSS: {e}")

    def aplicar_idioma(self, novo_idioma: str):
        logging.info(f"Idioma alterado para: {novo_idioma}")
        # QTranslator será implementado aqui futuramente

    # --- Lógica de Fluxos e Projetos ---

    def iniciar_novo_fluxo(self, caminho_json: str):
        """Prepara o workspace para um novo paciente baseado em um fluxo JSON."""
        try:
            config = self._carregar_configuracao(Path(caminho_json))
            self._configurar_fluxo_trabalho(config)
            self.stack.setCurrentWidget(self.workspace)
        except Exception as e:
            self._notificar_erro("Falha ao iniciar novo fluxo", e)

    def abrir_projeto_existente(self, caminho_pasta: str, modo: str):
        """Retoma um projeto salvo no disco."""
        try:
            pasta_projeto = Path(caminho_pasta)
            info_projeto = self._carregar_configuracao(pasta_projeto / "projeto" / "info.json")

            # Tenta encontrar o fluxo original que gerou este projeto
            nome_fluxo = info_projeto.get("fluxo_origem", "ortog.json")
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
        """Limpa o workspace e carrega os módulos dinamicamente."""
        self.workspace.clear()
        self.pasta_paciente_atual = None
        self.fluxo = FluxoBase(dados)

        for id_modulo in self.fluxo.sequencia:
            instancia = ModuloFactory.carregar_modulo(id_modulo)
            if instancia:
                # Conecta o sinal de conclusão do módulo para avançar a aba
                instancia.concluido.connect(self._on_modulo_concluido)
                self.workspace.adicionar_modulo(id_modulo, instancia)

    def _on_modulo_concluido(self):
        """Callback acionado quando um módulo termina seu processamento."""
        modulo_emissor = self.sender()
        if hasattr(modulo_emissor, 'pasta_paciente'):
            self.pasta_paciente_atual = modulo_emissor.pasta_paciente

        if self.workspace.avancar_aba() and self.pasta_paciente_atual:
            self._inicializar_modulo_ativo()

    def _inicializar_modulo_ativo(self):
        """Passa o contexto do paciente para o módulo que acabou de ser focado."""
        proximo_modulo = self.workspace.get_modulo_ativo()
        if proximo_modulo:
            proximo_modulo.inicializar(self.pasta_paciente_atual)

    def _notificar_erro(self, titulo: str, erro: Exception):
        logging.error(f"{titulo}: {erro}")
        QtWidgets.QMessageBox.critical(self, "Erro de Sistema", f"{titulo}\n\nDetalhes: {erro}")


# --- Ponto de Entrada ---

if __name__ == "__main__":
    # Configurações de DPI e Identificação no Windows
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

    app = QtWidgets.QApplication(sys.argv)

    # Define o estilo base antes de aplicar o QSS
    app.setStyle("Fusion")

    # Carrega o tema inicial (Escuro por padrão)
    tema_padrao = Path("temas") / "escuro_moderno.qss"
    if tema_padrao.exists():
        app.setStyleSheet(tema_padrao.read_text(encoding="utf-8"))
    else:
        logging.warning("Tema padrão não encontrado. Usando estilo nativo.")

    main_win = MainWindow()
    main_win.show()

    sys.exit(app.exec())