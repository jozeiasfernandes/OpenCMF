import json
import logging
from pathlib import Path
from typing import Dict, Any
from PySide6 import QtWidgets, QtCore, QtGui
from gui.cmf_creditos import Janela_Creditos

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
        PASTA_PACIENTES.mkdir(exist_ok=True)
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

        self.btn_cmf = QtWidgets.QPushButton()
        self.btn_cmf.setFixedSize(90, 40)
        self.btn_cmf.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cmf.setStyleSheet("background: transparent; border: none;")

        path_icones = Path(__file__).parent.parent / "icones"

        caminho_cmf = path_icones / "OpenCFM_Logo_Branco.png"
        if caminho_cmf.exists():
            self.btn_cmf.setIcon(QtGui.QIcon(str(caminho_cmf)))
            self.btn_cmf.setIconSize(QtCore.QSize(80, 50))

        self.btn_cmf.clicked.connect(self._abrir_creditos)
        layout.addWidget(self.btn_cmf)

        layout.addStretch()

        self.btn_settings = QtWidgets.QPushButton()
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.setFixedSize(40, 40)
        self.btn_settings.setCursor(QtCore.Qt.PointingHandCursor)

        caminho_config = path_icones / "config.png"
        if caminho_config.exists():
            self.btn_settings.setIcon(QtGui.QIcon(str(caminho_config)))
            self.btn_settings.setIconSize(QtCore.QSize(24, 24))
        else:
            self.btn_settings.setText("⚙")

        self.btn_settings.clicked.connect(self.config_solicitada.emit)
        layout.addWidget(self.btn_settings)

        return painel

    def _abrir_creditos(self):
        self.janela_creditos = Janela_Creditos(self)
        self.janela_creditos.exec()

    def atualizar_listas(self):
        self._carregar_projetos_do_disco()
        self._carregar_fluxos_do_disco()

    def _carregar_projetos_do_disco(self):
        self.lista_projetos.clear()
        if not PASTA_PACIENTES.exists():
            return

        for info_path in PASTA_PACIENTES.glob("**/info.json"):
            try:
                dados = json.loads(info_path.read_text(encoding="utf-8"))
                nome = dados.get("paciente", {}).get("nome", "Desconhecido")
                item = QtWidgets.QListWidgetItem(nome)
                item.setData(QtCore.Qt.UserRole, str(info_path.parent))
                self.lista_projetos.addItem(item)
            except Exception as e:
                logging.error(f"Erro no projeto {info_path.name}: {e}")

    def _carregar_fluxos_do_disco(self):
        while self.layout_cards.count():
            item = self.layout_cards.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not PASTA_FLUXOS.exists():
            return

        for path in PASTA_FLUXOS.glob("*.json"):
            if path.name == Path(FLUXO_CADASTRO).name:
                continue
            try:
                dados = json.loads(path.read_text(encoding="utf-8"))
                card = self._gerar_widget_card(dados, str(path))
                self.layout_cards.addWidget(card)
            except Exception as e:
                logging.error(f"Erro no fluxo {path.name}: {e}")

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
        self.btn_novo_projeto.clicked.connect(lambda: self.fluxo_escolhido.emit(FLUXO_CADASTRO))

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

    def _gerar_widget_card(self, dados: Dict[str, Any], caminho: str) -> QtWidgets.QFrame:
        card = QtWidgets.QFrame()
        card.setObjectName("card_container")
        card.setCursor(QtCore.Qt.PointingHandCursor)

        layout_h = QtWidgets.QHBoxLayout(card)
        layout_h.setContentsMargins(8, 8, 8, 8)
        layout_h.setSpacing(12)

        cor = dados.get("cor_fundo", {"r": 52, "g": 73, "b": 94})

        layout_h.addWidget(self._criar_bloco_destaque(dados.get("nome", "Sem Nome"), cor))

        for modulo in dados.get("sequencia", []):
            layout_h.addWidget(self._criar_bloco_modulo(modulo, cor))

        layout_h.addStretch()
        card.mousePressEvent = lambda _: self.fluxo_escolhido.emit(caminho)
        return card

    def _criar_bloco_destaque(self, texto: str, cor: Dict[str, int]) -> QtWidgets.QFrame:
        bloco = QtWidgets.QFrame()
        bloco.setFixedSize(180, 80)
        bloco.setStyleSheet(
            f"background-color: rgb({cor['r']}, {cor['g']}, {cor['b']}); "
            f"border-radius: 6px;"
        )

        lay = QtWidgets.QVBoxLayout(bloco)
        lbl = QtWidgets.QLabel(texto)
        lbl.setObjectName("label_fluxo")
        lbl.setWordWrap(True)
        lbl.setAlignment(QtCore.Qt.AlignCenter)

        lay.addWidget(lbl)
        return bloco

    def _criar_bloco_modulo(self, texto: str, cor: Dict[str, int]) -> QtWidgets.QLabel:
        lbl = QtWidgets.QLabel(texto)
        lbl.setObjectName("label_modulo")
        lbl.setFixedSize(130, 80)
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setStyleSheet(
            f"background-color: rgba({cor['r']}, {cor['g']}, {cor['b']}, 150); "
            f"border-radius: 6px;"
        )
        return lbl

    def _ao_clicar_projeto(self, item):
        self.projeto_selecionado.emit(item.data(QtCore.Qt.UserRole), "abrir")