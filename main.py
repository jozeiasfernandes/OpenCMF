# main.py

import sys
import json
import logging
import ctypes
from pathlib import Path
from typing import Dict, Any, List, Optional

from PySide6 import QtWidgets, QtCore, QtGui

from core.base import FluxoBase
from core.factory import ModuloFactory
from core.settings import settings
from gui.tela_inicial import Tela_Inicial
from gui.workspace import WorkspaceManager
from gui.editor_fluxo import PaginaEditorFluxo
from gui.config import PaginaConfig


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.pasta_paciente_atual: Optional[str] = None
        self.modulos_instanciados: List[Any] = []
        self.fluxo: Optional[FluxoBase] = None

        # Define a base do projeto para caminhos relativos robustos
        self.base_dir = Path(__file__).parent.resolve()

        self._setup_ui()
        self._setup_connections()

        # Carrega o tema imediatamente
        self._carregar_configuracoes_iniciais()

    def _setup_ui(self):
        titulo = settings.get("app_info", "titulo", "OpenCMF")
        self.setWindowTitle(titulo)
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
        caminho_icone = self.base_dir / "icones" / "cmf.png"
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
        self.workspace.currentChanged.connect(self._inicializar_modulo_ativo)

    def _carregar_configuracoes_iniciais(self):
        """Busca o tema na pasta raiz 'temas/' conforme estrutura do projeto."""
        tema_salvo = settings.get("preferencias", "tema", "dark")

        # CORREÇÃO DE CAMINHO: Removido 'gui/' pois a pasta está na raiz
        caminho_qss = self.base_dir / "temas" / f"{tema_salvo}.qss"

        if caminho_qss.exists():
            try:
                qss_content = caminho_qss.read_text(encoding="utf-8")
                QtWidgets.QApplication.instance().setStyleSheet(qss_content)
                print(f">>> [TEMA] Aplicado: {tema_salvo}")
            except Exception as e:
                logging.error(f"Erro ao carregar tema inicial: {e}")
        else:
            print(f">>> [AVISO] Arquivo não encontrado: {caminho_qss}")

    def aplicar_tema(self, caminho_qss: str):
        """Aplica o tema e salva o nome (stem) no config.json."""
        path = Path(caminho_qss)
        if path.exists():
            try:
                qss_content = path.read_text(encoding="utf-8")
                QtWidgets.QApplication.instance().setStyleSheet(qss_content)

                # Salva apenas o nome do arquivo (ex: 'roxo')
                settings.set("preferencias", "tema", path.stem)
                settings.save()
            except Exception as e:
                self._notificar_erro("Erro ao aplicar tema", e)

    def exibir_home(self):
        self.home.atualizar_listas()
        self.stack.setCurrentWidget(self.home)

    def selecionar_paciente(self, caminho_pasta: str, modo: str):
        self.pasta_paciente_atual = str(Path(caminho_pasta).resolve())

    def iniciar_fluxo_trabalho(self, caminho_json: str):
        path_fluxo = Path(caminho_json)
        is_cadastro = "cadastro" in path_fluxo.name.lower()

        if not is_cadastro and not self.pasta_paciente_atual:
            QtWidgets.QMessageBox.warning(self, "Atenção", "Selecione um paciente na lista.")
            return

        try:
            dados = json.loads(path_fluxo.read_text(encoding="utf-8"))
            self._configurar_workspace(dados)
            self.stack.setCurrentWidget(self.workspace)
            self._inicializar_modulo_ativo()
        except Exception as e:
            self._notificar_erro("Falha ao carregar fluxo", e)

    def _configurar_workspace(self, dados: Dict[str, Any]):
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

        self.workspace.blockSignals(False)

    def _inicializar_modulo_ativo(self):
        modulo = self.workspace.get_modulo_ativo()
        if not modulo:
            return

        self.workspace.blockSignals(True)
        try:
            if self.pasta_paciente_atual:
                sucesso, msg = modulo.verificar_pre_requisitos()
                if sucesso:
                    modulo.inicializar(self.pasta_paciente_atual)
                else:
                    QtWidgets.QMessageBox.warning(self, "Pré-requisitos", msg)
        finally:
            self.workspace.blockSignals(False)

    def _on_modulo_concluido(self):
        modulo_origem = self.sender()
        if hasattr(modulo_origem, 'pasta_paciente') and modulo_origem.pasta_paciente:
            self.pasta_paciente_atual = str(Path(modulo_origem.pasta_paciente).resolve())

        if not self.workspace.avancar_aba():
            self.exibir_home()

    def _notificar_erro(self, titulo: str, erro: Exception):
        logging.error(f"{titulo}: {erro}", exc_info=True)
        QtWidgets.QMessageBox.critical(self, "Erro", f"<b>{titulo}</b><br><br>{str(erro)}")


if __name__ == "__main__":
    app_id = settings.get("app_info", "id", "opencmf.surgicalplanning.1.0")
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    janela_principal = MainWindow()
    janela_principal.show()

    sys.exit(app.exec())