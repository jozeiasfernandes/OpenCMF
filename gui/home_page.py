import sys
import os
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from gui.paginas_extras.tela_creditos import Janela_Creditos
from gui.fluxo.fluxo_card import FluxoCard
from gui.logic.project_manager import ProjectManager


def get_resource_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent


def get_data_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


BASE_DIR = get_resource_path()
DATA_DIR = get_data_path()

PASTA_PACIENTES = DATA_DIR / "patients"
PASTA_FLUXOS = BASE_DIR / "flows"
PASTA_ICONES = BASE_DIR / "icons"

PASTA_PACIENTES.mkdir(exist_ok=True)
FLUXO_CADASTRO = str(PASTA_FLUXOS / "cadastro_novo_paciente.json")


class Tela_Inicial(QtWidgets.QWidget):
    projeto_selecionado = QtCore.Signal(str, str)
    fluxo_escolhido = QtCore.Signal(str)
    editor_solicitado = QtCore.Signal()
    config_solicitada = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.manager = ProjectManager(PASTA_PACIENTES, PASTA_FLUXOS)
        self.init_ui()
        self.atualizar_listas()

    def init_ui(self):
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(10, 50, 10, 10)
        self.layout_principal.setSpacing(10)

        self.layout_principal.addWidget(self.criar_barra_superior())
        self.layout_principal.addWidget(self.criar_secao_projetos())
        self.layout_principal.addWidget(self.criar_secao_fluxos())

    def atualizar_listas(self):
        self.listar_projetos()
        self.listar_fluxos()

    def criar_barra_superior(self) -> QtWidgets.QFrame:
        painel = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(painel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_logo = QtWidgets.QPushButton()
        self.btn_logo.setFixedSize(120, 40)
        self.btn_logo.setCursor(QtCore.Qt.PointingHandCursor)

        caminho_logo = PASTA_ICONES / "OpenCFM_Logo_Branco.png"
        if caminho_logo.exists():
            self.btn_logo.setIcon(QtGui.QIcon(str(caminho_logo)))
            self.btn_logo.setIconSize(QtCore.QSize(110, 40))
        else:
            self.btn_logo.setText("OpenCMF")

        self.btn_logo.clicked.connect(self.abrir_creditos)

        self.btn_config = QtWidgets.QPushButton()
        self.btn_config.setObjectName("btn_settings")
        self.btn_config.setFixedSize(40, 40)
        self.btn_config.setCursor(QtCore.Qt.PointingHandCursor)

        caminho_config = PASTA_ICONES / "config.png"
        if caminho_config.exists():
            self.btn_config.setIcon(QtGui.QIcon(str(caminho_config)))
            self.btn_config.setIconSize(QtCore.QSize(24, 24))
        else:
            self.btn_config.setText("⚙")

        self.btn_config.clicked.connect(self.config_solicitada.emit)

        layout.addWidget(self.btn_logo)
        layout.addStretch()
        layout.addWidget(self.btn_config)

        return painel

    def abrir_creditos(self):
        self.janela_creditos = Janela_Creditos(self)
        self.janela_creditos.exec()

    def criar_secao_projetos(self) -> QtWidgets.QFrame:
        painel = QtWidgets.QFrame()
        painel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(painel)

        cabecalho = QtWidgets.QHBoxLayout()
        cabecalho.addWidget(QtWidgets.QLabel("<h3>Projetos recentes</h3>"))
        cabecalho.addStretch()

        self.btn_novo_projeto = QtWidgets.QPushButton("Novo projeto")
        self.btn_novo_projeto.setObjectName("btn_novo_projeto")
        self.btn_novo_projeto.setFixedSize(150, 35)
        self.btn_novo_projeto.clicked.connect(
            lambda: self.fluxo_escolhido.emit(FLUXO_CADASTRO)
        )

        self.btn_excluir_projeto = QtWidgets.QPushButton("Excluir")
        self.btn_excluir_projeto.setObjectName("btn_remover_projeto")
        self.btn_excluir_projeto.setFixedSize(150, 35)
        self.btn_excluir_projeto.setStyleSheet("""
            QPushButton#btn_remover_projeto { 
                background-color: #f05748; color: white; font-weight: bold; border-radius: 4px; 
            }
            QPushButton#btn_remover_projeto:hover { background-color: #e74c3c; }
        """)
        self.btn_excluir_projeto.clicked.connect(self.ao_solicitar_exclusao)

        cabecalho.addWidget(self.btn_novo_projeto)
        cabecalho.addWidget(self.btn_excluir_projeto)

        self.view_projetos = QtWidgets.QListWidget()
        self.view_projetos.setMinimumHeight(150)
        self.view_projetos.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view_projetos.customContextMenuRequested.connect(self.abrir_menu_contexto)
        self.view_projetos.itemDoubleClicked.connect(self.ao_abrir_projeto)

        layout.addLayout(cabecalho)
        layout.addWidget(self.view_projetos)
        return painel

    def listar_projetos(self):
        self.view_projetos.clear()
        try:
            projetos = self.manager.listar_projetos_recentes()
            for dados in projetos:
                info = dados.get("paciente") or {}
                nome = info.get("nome") or Path(dados.get("_caminho_local", "")).name

                item = QtWidgets.QListWidgetItem(nome or "Paciente sem nome")
                item.setData(QtCore.Qt.UserRole, dados.get("_caminho_local"))
                self.view_projetos.addItem(item)
        except Exception as e:
            print(f"Falha ao listar projetos: {e}")

    def ao_abrir_projeto(self, item):
        self.projeto_selecionado.emit(item.data(QtCore.Qt.UserRole), "abrir")

    def ao_solicitar_exclusao(self):
        item = self.view_projetos.currentItem()
        if not item:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um projeto para excluir.")
            return
        self.confirmar_exclusao_projeto(item)

    def abrir_menu_contexto(self, posicao):
        item = self.view_projetos.itemAt(posicao)
        if not item:
            return

        menu = QtWidgets.QMenu()
        acao_abrir = menu.addAction("Abrir Projeto")
        acao_remover = menu.addAction("Remover Projeto")
        acao_remover.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))

        escolha = menu.exec(self.view_projetos.mapToGlobal(posicao))

        if escolha == acao_abrir:
            self.ao_abrir_projeto(item)
        elif escolha == acao_remover:
            self.confirmar_exclusao_projeto(item)

    def confirmar_exclusao_projeto(self, item):
        caminho = item.data(QtCore.Qt.UserRole)
        resposta = QtWidgets.QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Deseja apagar permanentemente o projeto: {item.text()}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if resposta == QtWidgets.QMessageBox.Yes:
            if self.manager.remover_projeto(caminho):
                self.listar_projetos()
            else:
                QtWidgets.QMessageBox.critical(self, "Erro", "Falha ao remover pasta do projeto.")

    def criar_secao_fluxos(self) -> QtWidgets.QFrame:
        painel = QtWidgets.QFrame()
        painel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(painel)

        cabecalho = QtWidgets.QHBoxLayout()
        cabecalho.addWidget(QtWidgets.QLabel("<h3>Fluxos Disponíveis</h3>"))
        cabecalho.addStretch()

        btn_novo_fluxo = QtWidgets.QPushButton("Novo fluxo")
        btn_novo_fluxo.setFixedSize(150, 35)
        btn_novo_fluxo.clicked.connect(self.editor_solicitado.emit)

        cabecalho.addWidget(btn_novo_fluxo)

        self.scroll_fluxos = QtWidgets.QScrollArea()
        self.scroll_fluxos.setWidgetResizable(True)
        self.scroll_fluxos.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.container_cards = QtWidgets.QWidget()
        self.layout_cards = QtWidgets.QVBoxLayout(self.container_cards)
        self.layout_cards.setAlignment(QtCore.Qt.AlignTop)
        self.layout_cards.setSpacing(10)
        self.layout_cards.setContentsMargins(5, 5, 5, 5)

        self.scroll_fluxos.setWidget(self.container_cards)
        layout.addLayout(cabecalho)
        layout.addWidget(self.scroll_fluxos)
        return painel

    def listar_fluxos(self):
        while self.layout_cards.count():
            widget = self.layout_cards.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        try:
            fluxos = self.manager.listar_fluxos_disponiveis(ignorar_nome=FLUXO_CADASTRO)
            for dados in fluxos:
                card = FluxoCard(dados, dados["_caminho_arquivo"])
                card.clicado.connect(self.fluxo_escolhido.emit)
                if hasattr(card, 'exclusao_solicitada'):
                    card.exclusao_solicitada.connect(self.confirmar_exclusao_fluxo)
                self.layout_cards.addWidget(card)
            self.layout_cards.addStretch()
        except Exception as e:
            print(f"Falha ao listar flows: {e}")

    def confirmar_exclusao_fluxo(self, caminho_arquivo):
        resposta = QtWidgets.QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Apagar o fluxo: {Path(caminho_arquivo).stem}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if resposta == QtWidgets.QMessageBox.Yes:
            if self.manager.remover_fluxo(caminho_arquivo):
                self.listar_fluxos()