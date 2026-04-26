import sys
import json
import logging
import ctypes
from pathlib import Path
from typing import Dict, Any, List, Optional
from PySide6 import QtWidgets, QtCore, QtGui

from core.base_module.base import FluxoBase
from core.base_module.factory import ModuloFactory
from gui.settings import settings
from gui.home_page import Tela_Inicial
from core.workspace import WorkspaceManager
from gui.fluxo.flow_editor import PaginaEditorFluxo
from gui.paginas_extras.settings_page import PaginaConfig

import vtk

vtk.vtkObject.GlobalWarningDisplayOff()
vtk.vtkOutputWindow.GetInstance().SetInstance(vtk.vtkFileOutputWindow())
vtk_log = vtk.vtkFileOutputWindow()
vtk_log.SetFileName("vtk_debug.log")
vtk.vtkOutputWindow.GetInstance().SetInstance(vtk_log)


def get_resource_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.resolve()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.pasta_paciente_atual: Optional[str] = None
        self.modulos_instanciados: List[Any] = []
        self.fluxo: Optional[FluxoBase] = None

        self.base_dir = get_resource_path()

        self.init_interface()
        self.conectar_eventos()
        self.carregar_preferencias()

    def init_interface(self):
        titulo = settings.get("app_info", "titulo", "OpenCMF")
        self.setWindowTitle(titulo)
        self.setGeometry(150, 50, 1024, 650)

        self.configurar_icone_janela()

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

    def configurar_icone_janela(self):
        caminho_icone = self.base_dir / "icons" / "cmf.png"
        if caminho_icone.exists():
            icone = QtGui.QIcon(str(caminho_icone))
            self.setWindowIcon(icone)
            QtWidgets.QApplication.setWindowIcon(icone)

    def conectar_eventos(self):
        self.home.projeto_selecionado.connect(self.ao_selecionar_paciente)
        self.home.fluxo_escolhido.connect(self.iniciar_fluxo_trabalho)
        self.home.editor_solicitado.connect(lambda: self.stack.setCurrentWidget(self.editor_fluxo))
        self.home.config_solicitada.connect(lambda: self.stack.setCurrentWidget(self.config))

        self.editor_fluxo.voltar_solicitado.connect(self.retornar_para_home)
        self.workspace.home_solicitada.connect(self.retornar_para_home)
        self.config.voltar_solicitado.connect(self.retornar_para_home)

        self.config.tema_alterado.connect(self.aplicar_tema_visual)
        self.workspace.currentChanged.connect(self.sincronizar_estado_modulo)

    def carregar_preferencias(self):
        tema = settings.get("preferencias", "tema", "dark")
        caminho_qss = self.base_dir / "themes" / f"{tema}.qss"
        self.aplicar_tema_visual(str(caminho_qss))

    def aplicar_tema_visual(self, caminho_qss: str):
        arquivo_qss = Path(caminho_qss)
        if not arquivo_qss.exists():
            return

        try:
            estilo = arquivo_qss.read_text(encoding="utf-8")
            QtWidgets.QApplication.instance().setStyleSheet(estilo)
            settings.set("preferencias", "tema", arquivo_qss.stem)
            settings.save()
        except Exception as e:
            self.exibir_erro_critico("Erro de Estilização", e)

    def retornar_para_home(self):
        self.home.atualizar_listas()
        self.stack.setCurrentWidget(self.home)

    def ao_selecionar_paciente(self, caminho_pasta: str, modo: str):
        self.pasta_paciente_atual = str(Path(caminho_pasta).resolve())

    def iniciar_fluxo_trabalho(self, caminho_json: str):
        arquivo_fluxo = Path(caminho_json)
        eh_cadastro = "cadastro" in arquivo_fluxo.name.lower()

        if not eh_cadastro and not self.pasta_paciente_atual:
            QtWidgets.QMessageBox.warning(self, "Atenção", "Selecione um paciente antes de prosseguir.")
            return

        try:
            config_fluxo = json.loads(arquivo_fluxo.read_text(encoding="utf-8"))
            self.montar_area_trabalho(config_fluxo)
            self.stack.setCurrentWidget(self.workspace)
            QtCore.QTimer.singleShot(100, self.sincronizar_estado_modulo)
        except Exception as e:
            self.exibir_erro_critico("Falha ao carregar Fluxo", e)

    def montar_area_trabalho(self, dados: Dict[str, Any]):
        self.workspace.blockSignals(True)
        self.workspace.clear()
        self.modulos_instanciados.clear()

        self.fluxo = FluxoBase(dados)

        for id_modulo in self.fluxo.sequencia:
            modulo = ModuloFactory.carregar_modulo(id_modulo)
            if modulo:
                modulo.concluido.connect(self.ao_concluir_etapa)
                self.modulos_instanciados.append(modulo)
                self.workspace.adicionar_modulo(id_modulo, modulo)

        self.workspace.blockSignals(False)

    def sincronizar_estado_modulo(self):
        modulo = self.workspace.get_modulo_ativo()
        if not modulo or not self.pasta_paciente_atual:
            return

        modulo.pasta_paciente = self.pasta_paciente_atual
        apto, mensagem = modulo.verificar_pre_requisitos()

        if apto:
            modulo.inicializar(self.pasta_paciente_atual)
        else:
            if "cadastro" not in modulo.__class__.__name__.lower():
                QtWidgets.QMessageBox.warning(self, "Requisito Faltante", mensagem)

    def ao_concluir_etapa(self):
        emissor = self.sender()
        if hasattr(emissor, 'pasta_paciente') and emissor.pasta_paciente:
            self.pasta_paciente_atual = str(Path(emissor.pasta_paciente).resolve())

    def exibir_erro_critico(self, titulo: str, erro: Exception):
        logging.error(f"{titulo}: {erro}", exc_info=True)
        QtWidgets.QMessageBox.critical(self, "Erro Crítico", f"<b>{titulo}</b><br>{str(erro)}")


if __name__ == "__main__":
    id_aplicativo = settings.get("app_info", "id", "opencmf.surgicalplanning.1.0")
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(id_aplicativo)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    janela = MainWindow()
    janela.show()

    sys.exit(app.exec())