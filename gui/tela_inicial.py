import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from gui.cmf_creditos import Janela_Creditos
from gui.widgets.fluxo_card import FluxoCard
from gui.logic.project_manager import ProjectManager

PASTA_PACIENTES = Path("pacientes")
PASTA_FLUXOS = Path("fluxos")
FLUXO_CADASTRO = str(PASTA_FLUXOS / "cadastro_novo_paciente.json")


class Tela_Inicial(QtWidgets.QWidget):
    projeto_selecionado = QtCore.Signal(str, str)
    fluxo_escolhido = QtCore.Signal(str)
    editor_solicitado = QtCore.Signal()
    config_solicitada = QtCore.Signal()

    def __init__(self):
        super().__init__()
        # Inicializa o gerenciador de lógica
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

        # Logo / Botão Créditos
        self.btn_cmf = QtWidgets.QPushButton()
        self.btn_cmf.setFixedSize(90, 40)
        self.btn_cmf.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cmf.setStyleSheet("background: transparent; border: none;")

        path_icones = Path(__file__).parent.parent / "icones"
        logo_path = path_icones / "OpenCFM_Logo_Branco.png"

        if logo_path.exists():
            self.btn_cmf.setIcon(QtGui.QIcon(str(logo_path)))
            self.btn_cmf.setIconSize(QtCore.QSize(80, 50))

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

        self.btn_novo_projeto = QtWidgets.QPushButton("+ NOVO PROJETO")
        self.btn_novo_projeto.setObjectName("btn_novo_projeto")
        self.btn_novo_projeto.setProperty("class", "botao-acao")
        self.btn_novo_projeto.setFixedSize(180, 40)
        self.btn_novo_projeto.clicked.connect(
            lambda: self.fluxo_escolhido.emit(FLUXO_CADASTRO)
        )

        header.addWidget(self.btn_novo_projeto)

        self.lista_projetos = QtWidgets.QListWidget()
        self.lista_projetos.setMinimumHeight(120)
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

        btn_novo_fluxo = QtWidgets.QPushButton("CRIAR NOVO FLUXO")
        btn_novo_fluxo.setProperty("class", "botao-acao")
        btn_novo_fluxo.setFixedSize(180, 40)
        btn_novo_fluxo.clicked.connect(self.editor_solicitado.emit)

        header.addWidget(btn_novo_fluxo, alignment=QtCore.Qt.AlignRight)

        self.scroll_fluxos = QtWidgets.QScrollArea()
        self.scroll_fluxos.setWidgetResizable(True)
        self.scroll_fluxos.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.container_cards = QtWidgets.QWidget()
        self.layout_cards = QtWidgets.QVBoxLayout(self.container_cards)
        self.layout_cards.setAlignment(QtCore.Qt.AlignTop)
        self.layout_cards.setSpacing(10)

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
            # Usamos a chave auxiliar criada no ProjectManager
            item.setData(QtCore.Qt.UserRole, proj.get("_caminho_local"))
            self.lista_projetos.addItem(item)

    def _carregar_fluxos(self):
        # Limpa widgets antigos
        while self.layout_cards.count():
            item = self.layout_cards.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        fluxos = self.manager.listar_fluxos_disponiveis(ignorar_arquivo=FLUXO_CADASTRO)

        for dados in fluxos:
            # Instancia o card refatorado
            card = FluxoCard(dados, dados["_caminho_arquivo"])
            card.clicado.connect(self.fluxo_escolhido.emit)
            self.layout_cards.addWidget(card)

    def _abrir_creditos(self):
        self.janela_creditos = Janela_Creditos(self)
        self.janela_creditos.exec()

    def _ao_clicar_projeto(self, item):
        self.projeto_selecionado.emit(item.data(QtCore.Qt.UserRole), "abrir")