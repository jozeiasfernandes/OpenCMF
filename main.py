import sys
import json
import logging
import ctypes
from pathlib import Path
from typing import Dict, Any, List, Optional
from PySide6 import QtWidgets, QtCore, QtGui

from core.modulo_base.base import FluxoBase
from core.modulo_base.factory import ModuloFactory
from core.settings import settings
from gui.tela_inicial import Tela_Inicial
from gui.workspace import WorkspaceManager
from gui.fluxo.editor_fluxo import PaginaEditorFluxo
from gui.paginas_extras.tela_config import PaginaConfig

import vtk

vtk.vtkObject.GlobalWarningDisplayOff()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.pasta_paciente_atual: Optional[str] = None
        self.modulos_instanciados: List[Any] = []
        self.fluxo: Optional[FluxoBase] = None
        self.base_dir = Path(__file__).parent.resolve()

        self._interface()
        self._configurar_eventos()
        self._configs_user()

    def _interface(self):
        titulo = settings.get("app_info", "titulo", "OpenCMF")
        self.setWindowTitle(titulo)
        self.setGeometry(150, 50, 1024, 650)

        self._icone_janela()

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

    def _icone_janela(self):
        caminho_icone = self.base_dir / "icones" / "cmf.png"
        if caminho_icone.exists():
            icone = QtGui.QIcon(str(caminho_icone))
            self.setWindowIcon(icone)
            QtWidgets.QApplication.setWindowIcon(icone)

    def _configurar_eventos(self):
        self.home.projeto_selecionado.connect(self.select_paciente)
        self.home.fluxo_escolhido.connect(self.iniciar_fluxo_trabalho)
        self.home.editor_solicitado.connect(lambda: self.stack.setCurrentWidget(self.editor_fluxo))
        self.home.config_solicitada.connect(lambda: self.stack.setCurrentWidget(self.config))

        self.editor_fluxo.voltar_solicitado.connect(self.navegar_para_home)
        self.workspace.home_solicitada.connect(self.navegar_para_home)
        self.config.voltar_solicitado.connect(self.navegar_para_home)

        self.config.tema_alterado.connect(self.atualizar_estilo_visual)
        self.workspace.currentChanged.connect(self._sincronizar_modulo_visualizado)

    def _configs_user(self):
        tema = settings.get("preferencias", "tema", "dark")
        caminho_qss = self.base_dir / "temas" / f"{tema}.qss"
        self.atualizar_estilo_visual(str(caminho_qss))

    def atualizar_estilo_visual(self, caminho_qss: str):
        path = Path(caminho_qss)
        if not path.exists():
            return

        try:
            estilo = path.read_text(encoding="utf-8")
            QtWidgets.QApplication.instance().setStyleSheet(estilo)

            settings.set("preferencias", "tema", path.stem)
            settings.save()
        except Exception as e:
            self._alerta_erro("Erro de Estilização", e)

    def navegar_para_home(self):
        self.home.atualizar_listas()
        self.stack.setCurrentWidget(self.home)

    def select_paciente(self, caminho_pasta: str, modo: str):
        self.pasta_paciente_atual = str(Path(caminho_pasta).resolve())
        print(f">>> [PACIENTE] Ativo: {self.pasta_paciente_atual}")

    def iniciar_fluxo_trabalho(self, caminho_json: str):
        path_fluxo = Path(caminho_json)
        eh_cadastro = "cadastro" in path_fluxo.name.lower()

        if not eh_cadastro and not self.pasta_paciente_atual:
            QtWidgets.QMessageBox.warning(self, "Atenção", "Selecione um paciente antes de prosseguir.")
            return

        try:
            config_fluxo = json.loads(path_fluxo.read_text(encoding="utf-8"))

            self._montar_workspace(config_fluxo)
            self.stack.setCurrentWidget(self.workspace)

            QtCore.QTimer.singleShot(100, self._sincronizar_modulo_visualizado)
        except Exception as e:
            self._alerta_erro("Falha no Fluxo", e)

    def _montar_workspace(self, dados: Dict[str, Any]):
        self.workspace.blockSignals(True)
        self.workspace.clear()
        self.modulos_instanciados.clear()

        self.fluxo = FluxoBase(dados)

        for id_modulo in self.fluxo.sequencia:
            modulo = ModuloFactory.carregar_modulo(id_modulo)
            if modulo:
                modulo.concluido.connect(self._processar_conclusao_modulo)
                self.modulos_instanciados.append(modulo)
                self.workspace.adicionar_modulo(id_modulo, modulo)

        self.workspace.blockSignals(False)

    def _sincronizar_modulo_visualizado(self):
        modulo = self.workspace.get_modulo_ativo()
        if not modulo or not self.pasta_paciente_atual:
            return

        modulo.pasta_paciente = self.pasta_paciente_atual
        apto, mensagem = modulo.verificar_pre_requisitos()

        identificador = getattr(modulo, 'nome', modulo.__class__.__name__)

        if apto:
            print(f">>> [CORE] Inicializando: {identificador}")
            modulo.inicializar(self.pasta_paciente_atual)
        else:
            print(f">>> [AVISO] Bloqueio em {identificador}: {mensagem}")
            if "cadastro" not in identificador.lower():
                QtWidgets.QMessageBox.warning(self, "Requisito Faltante", mensagem)

    def _processar_conclusao_modulo(self):
        modulo_emissor = self.sender()

        if hasattr(modulo_emissor, 'pasta_paciente') and modulo_emissor.pasta_paciente:
            self.pasta_paciente_atual = str(Path(modulo_emissor.pasta_paciente).resolve())

        nome = getattr(modulo_emissor, 'nome', modulo_emissor.__class__.__name__)
        print(f">>> [FLUXO] Etapa concluída: {nome}")

    def _alerta_erro(self, titulo: str, erro: Exception):
        logging.error(f"{titulo}: {erro}", exc_info=True)
        QtWidgets.QMessageBox.critical(self, "Erro Crítico", f"<b>{titulo}</b><br>{str(erro)}")


if __name__ == "__main__":
    app_id = settings.get("app_info", "id", "opencmf.surgicalplanning.1.0")
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    janela = MainWindow()
    janela.show()

    sys.exit(app.exec())