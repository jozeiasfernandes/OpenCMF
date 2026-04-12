# Tela inicial

import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from gui.cmf_creditos import Janela_Creditos
from gui.widgets.fluxo_card import FluxoCard
from gui.logic.project_manager import ProjectManager

# Configuração de caminhos robusta
BASE_DIR = Path(__file__).parent.parent
PASTA_PACIENTES = BASE_DIR / "pacientes"
PASTA_FLUXOS = BASE_DIR / "fluxos"
# Mantemos como string para o Signal, mas Path para manipulação
FLUXO_CADASTRO = str(PASTA_FLUXOS / "cadastro_novo_paciente.json")


class Tela_Inicial(QtWidgets.QWidget):
    projeto_selecionado = QtCore.Signal(str, str)
    fluxo_escolhido = QtCore.Signal(str)
    editor_solicitado = QtCore.Signal()
    config_solicitada = QtCore.Signal()

    def __init__(self):
        super().__init__()
        # Inicializa o manager com caminhos Path
        self.manager = ProjectManager(PASTA_PACIENTES, PASTA_FLUXOS)
        self._setup_ui()
        self.atualizar_listas()

    def _setup_ui(self):
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(20, 10, 20, 20)
        self.layout_principal.setSpacing(20)

        self.layout_principal.addWidget(self._renderizar_barra_ferramentas())
        self.layout_principal.addWidget(self._renderizar_secao_projetos())
        self.layout_principal.addWidget(self._renderizar_secao_fluxos())

    def _renderizar_barra_ferramentas(self) -> QtWidgets.QFrame:
        painel = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(painel)
        layout.setContentsMargins(0, 0, 0, 0)

        path_icones = BASE_DIR / "icones"

        # Botão Logo/Créditos
        self.btn_cmf = QtWidgets.QPushButton()
        self.btn_cmf.setFixedSize(120, 40)
        self.btn_cmf.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cmf.setStyleSheet("background: transparent; border: none;")

        logo_path = path_icones / "OpenCFM_Logo_Branco.png"
        if logo_path.exists():
            self.btn_cmf.setIcon(QtGui.QIcon(str(logo_path)))
            self.btn_cmf.setIconSize(QtCore.QSize(110, 40))
        else:
            self.btn_cmf.setText("OpenCMF")

        self.btn_cmf.clicked.connect(self._abrir_creditos)
        layout.addWidget(self.btn_cmf)
        layout.addStretch()

        # Botão Configurações
        self.btn_settings = QtWidgets.QPushButton()
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.setFixedSize(40, 40)
        self.btn_settings.setCursor(QtCore.Qt.PointingHandCursor)

        config_path = path_icones / "config.png"
        if config_path.exists():
            self.btn_settings.setIcon(QtGui.QIcon(str(config_path)))
            self.btn_settings.setIconSize(QtCore.QSize(24, 24))
        else:
            self.btn_settings.setText("⚙")

        self.btn_settings.clicked.connect(self.config_solicitada.emit)
        layout.addWidget(self.btn_settings)

        return painel

    def _renderizar_secao_projetos(self) -> QtWidgets.QFrame:
        painel = QtWidgets.QFrame()
        painel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(painel)

        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel("<h3>Projetos recentes</h3>"))
        header.addStretch()

        self.btn_novo_projeto = QtWidgets.QPushButton("Novo projeto")
        self.btn_novo_projeto.setObjectName("btn_novo_projeto")
        self.btn_novo_projeto.setFixedSize(100, 30)
        self.btn_novo_projeto.clicked.connect(
            lambda: self.fluxo_escolhido.emit(FLUXO_CADASTRO)
        )

        self.btn_remover_projeto = QtWidgets.QPushButton("Excluir")
        self.btn_remover_projeto.setObjectName("btn_remover_projeto")
        self.btn_remover_projeto.setFixedSize(100, 30)
        self.btn_remover_projeto.setStyleSheet("""
            QPushButton#btn_remover_projeto {
                background-color: #c0392b;
                color: white;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton#btn_remover_projeto:hover { background-color: #e74c3c; }
        """)
        self.btn_remover_projeto.clicked.connect(self._ao_clicar_remover_botao)

        header.addWidget(self.btn_novo_projeto)
        header.addWidget(self.btn_remover_projeto)

        self.lista_projetos = QtWidgets.QListWidget()
        self.lista_projetos.setMinimumHeight(150)
        self.lista_projetos.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lista_projetos.customContextMenuRequested.connect(self._mostrar_menu_contexto)
        self.lista_projetos.itemDoubleClicked.connect(self._ao_clicar_projeto)

        layout.addLayout(header)
        layout.addWidget(self.lista_projetos)
        return painel

    def _renderizar_secao_fluxos(self) -> QtWidgets.QFrame:
        painel = QtWidgets.QFrame()
        painel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(painel)

        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel("<h3>Fluxos Disponíveis</h3>"))
        header.addStretch()

        btn_novo_fluxo = QtWidgets.QPushButton("Novo fluxo")
        btn_novo_fluxo.setFixedSize(100, 30)
        btn_novo_fluxo.clicked.connect(self.editor_solicitado.emit)

        header.addWidget(btn_novo_fluxo)

        self.scroll_fluxos = QtWidgets.QScrollArea()
        self.scroll_fluxos.setWidgetResizable(True)
        self.scroll_fluxos.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.container_cards = QtWidgets.QWidget()
        self.layout_cards = QtWidgets.QVBoxLayout(self.container_cards)
        self.layout_cards.setAlignment(QtCore.Qt.AlignTop)
        self.layout_cards.setSpacing(10)
        self.layout_cards.setContentsMargins(5, 5, 5, 5)

        self.scroll_fluxos.setWidget(self.container_cards)
        layout.addLayout(header)
        layout.addWidget(self.scroll_fluxos)
        return painel

    def atualizar_listas(self):
        self._carregar_projetos()
        self._carregar_fluxos()

    def _carregar_projetos(self):
        self.lista_projetos.clear()
        projetos = self.manager.listar_projetos_recentes()
        for proj in projetos:
            nome = proj.get("paciente", {}).get("nome", "Desconhecido")
            item = QtWidgets.QListWidgetItem(nome)
            item.setData(QtCore.Qt.UserRole, proj.get("_caminho_local"))
            self.lista_projetos.addItem(item)

    def _carregar_fluxos(self):
        while self.layout_cards.count():
            item = self.layout_cards.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # CORREÇÃO: ignorar_arquivo -> ignorar_nome conforme a nova ProjectManager
        fluxos = self.manager.listar_fluxos_disponiveis(ignorar_nome=FLUXO_CADASTRO)

        for dados in fluxos:
            card = FluxoCard(dados, dados["_caminho_arquivo"])
            card.clicado.connect(self.fluxo_escolhido.emit)
            if hasattr(card, 'exclusao_solicitada'):
                card.exclusao_solicitada.connect(self._confirmar_remocao_fluxo)

            self.layout_cards.addWidget(card)

        self.layout_cards.addStretch()

    def _confirmar_remocao_fluxo(self, caminho_arquivo):
        nome_fluxo = Path(caminho_arquivo).stem
        pergunta = QtWidgets.QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Deseja apagar o fluxo: {nome_fluxo}?\nEsta ação não pode ser desfeita.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if pergunta == QtWidgets.QMessageBox.Yes:
            if self.manager.remover_fluxo(caminho_arquivo):
                self._carregar_fluxos()

    def _mostrar_menu_contexto(self, posicao):
        item = self.lista_projetos.itemAt(posicao)
        if not item: return
        menu = QtWidgets.QMenu()
        acao_abrir = menu.addAction("Abrir Projeto")
        acao_remover = menu.addAction("Remover Projeto")
        acao_remover.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))
        escolha = menu.exec(self.lista_projetos.mapToGlobal(posicao))
        if escolha == acao_abrir:
            self._ao_clicar_projeto(item)
        elif escolha == acao_remover:
            self._confirmar_remocao(item)

    def _ao_clicar_remover_botao(self):
        item_selecionado = self.lista_projetos.currentItem()
        if not item_selecionado:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um projeto na lista para excluir.")
            return
        self._confirmar_remocao(item_selecionado)

    def _confirmar_remocao(self, item):
        nome_paciente = item.text()
        caminho = item.data(QtCore.Qt.UserRole)
        pergunta = QtWidgets.QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Deseja apagar permanentemente o projeto de: {nome_paciente}?\nEsta ação não pode ser desfeita.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if pergunta == QtWidgets.QMessageBox.Yes:
            if self.manager.remover_projeto(caminho):
                self._carregar_projetos()
            else:
                QtWidgets.QMessageBox.critical(self, "Erro", "Não foi possível remover a pasta do projeto.")

    def _abrir_creditos(self):
        self.janela_creditos = Janela_Creditos(self)
        self.janela_creditos.exec()

    def _ao_clicar_projeto(self, item):
        self.projeto_selecionado.emit(item.data(QtCore.Qt.UserRole), "abrir")