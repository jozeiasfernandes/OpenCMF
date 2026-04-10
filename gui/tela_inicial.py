import json
import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

PASTA_PACIENTES = Path("pacientes")
PASTA_FLUXOS = Path("fluxos")
FLUXO_CADASTRO = str(PASTA_FLUXOS / "cadastro_novo_paciente.json")


class Tela_Inicial(QtWidgets.QWidget):
    projeto_selecionado = QtCore.Signal(str, str)
    fluxo_escolhido = QtCore.Signal(str)
    editor_solicitado = QtCore.Signal()

    def __init__(self):
        super().__init__()
        PASTA_PACIENTES.mkdir(exist_ok=True)
        self._configurar_layout_principal()
        self.atualizar_listas()

    # ---------------- UI ----------------

    def _configurar_layout_principal(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)  # ✔ ajuste visual
        layout.setSpacing(20)

        layout.addWidget(self.painel_ferramentas())
        layout.addWidget(self.painel_projetos())
        layout.addWidget(self.painel_fluxos())

    def painel_ferramentas(self):
        painel = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(painel)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addStretch()

        self.btn_settings = QtWidgets.QPushButton()
        self.btn_settings.setFixedSize(40, 40)
        self.btn_settings.setCursor(QtCore.Qt.PointingHandCursor)

        caminho_icon_config = Path(__file__).parent / "icones" / "config.png"

        if caminho_icon_config.exists():
            self.btn_settings.setIcon(QtGui.QIcon(str(caminho_icon_config)))
            self.btn_settings.setIconSize(QtCore.QSize(24, 24))
        else:
            self.btn_settings.setText("⚙")

        # ✔ estilo restaurado
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border-radius: 20px;
                color: white;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)

        layout.addWidget(self.btn_settings)
        return painel

    def painel_projetos(self):
        painel = QtWidgets.QFrame()
        painel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(painel)

        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel("<h3>Projetos recentes</h3>"))

        self.btn_novo_projeto = QtWidgets.QPushButton("+ NOVO PROJETO")
        self.btn_novo_projeto.setFixedSize(180, 40)
        self.btn_novo_projeto.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                font-weight: bold;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.btn_novo_projeto.clicked.connect(self._on_novo_projeto_clicked)
        header.addWidget(self.btn_novo_projeto)

        self.lista_projetos = QtWidgets.QListWidget()
        self.lista_projetos.setMinimumHeight(150)
        self.lista_projetos.setMaximumHeight(200)
        self.lista_projetos.itemDoubleClicked.connect(self._on_projeto_double_clicked)

        layout.addLayout(header)
        layout.addWidget(self.lista_projetos)
        return painel

    def painel_fluxos(self):
        painel = QtWidgets.QFrame()
        painel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(painel)

        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel("<h3>Fluxos</h3>"))

        btn_config_fluxo = QtWidgets.QPushButton("CRIAR NOVO FLUXO")
        btn_config_fluxo.setFixedSize(180, 40)
        btn_config_fluxo.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                font-weight: bold;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        btn_config_fluxo.clicked.connect(self.editor_solicitado.emit)
        header.addWidget(btn_config_fluxo, alignment=QtCore.Qt.AlignRight)

        self.scroll_fluxos = QtWidgets.QScrollArea()
        self.scroll_fluxos.setWidgetResizable(True)
        self.scroll_fluxos.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_fluxos.setMinimumHeight(250)

        self.container_cards = QtWidgets.QWidget()
        self.grid_fluxos = QtWidgets.QGridLayout(self.container_cards)
        self.grid_fluxos.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.scroll_fluxos.setWidget(self.container_cards)

        layout.addLayout(header)
        layout.addWidget(self.scroll_fluxos)
        return painel

    # ---------------- DADOS ----------------

    def atualizar_listas(self):
        self._popular_lista_projetos()
        self._popular_grid_fluxos()

    def _popular_lista_projetos(self):
        self.lista_projetos.clear()

        for arquivo_info in PASTA_PACIENTES.glob("**/info.json"):
            try:
                self._adicionar_item_projeto(arquivo_info)
            except Exception as e:
                logging.error(f"Erro ao processar projeto {arquivo_info}: {e}")

    def _adicionar_item_projeto(self, caminho_info: Path):
        dados = json.loads(caminho_info.read_text(encoding="utf-8"))

        paciente = dados.get("paciente", {})
        nome = paciente.get("nome", "Desconhecido")

        mtime = caminho_info.stat().st_mtime
        data_str = QtCore.QDateTime.fromSecsSinceEpoch(
            int(mtime)
        ).toString("dd/MM/yyyy")

        item = QtWidgets.QListWidgetItem(
            f"{nome.ljust(40)} | Última Edição: {data_str}"
        )

        # ✔ caminho correto do projeto
        item.setData(QtCore.Qt.UserRole, str(caminho_info.parent))

        self.lista_projetos.addItem(item)

    def _popular_grid_fluxos(self):
        self._limpar_grid_fluxos()

        if not PASTA_FLUXOS.exists():
            return

        arquivos = [
            f for f in PASTA_FLUXOS.glob("*.json")
            if f.name != Path(FLUXO_CADASTRO).name
        ]

        for i, arquivo in enumerate(arquivos):
            self._processar_arquivo_fluxo(arquivo, i)

    def _processar_arquivo_fluxo(self, arquivo: Path, index: int):
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            nome = dados.get("nome_fluxo", arquivo.stem.capitalize())

            card = self._criar_card_widget(nome, str(arquivo))
            self.grid_fluxos.addWidget(card, index // 4, index % 4)

        except Exception as e:
            logging.warning(f"Erro ao carregar fluxo {arquivo}: {e}")

    def _limpar_grid_fluxos(self):
        while self.grid_fluxos.count():
            item = self.grid_fluxos.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

    def _criar_card_widget(self, titulo: str, caminho: str):
        card = QtWidgets.QFrame()
        card.setFixedSize(180, 100)
        card.setCursor(QtCore.Qt.PointingHandCursor)

        # ✔ estilo restaurado
        card.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 8px;
                border: 1px solid #2c3e50;
            }
            QFrame:hover {
                background-color: #2c3e50;
                border: 1px solid #3498db;
            }
        """)

        layout = QtWidgets.QVBoxLayout(card)
        lbl = QtWidgets.QLabel(f"<b>{titulo}</b>")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setStyleSheet("color: white; border: none;")
        layout.addWidget(lbl)

        card.mousePressEvent = lambda _: self.fluxo_escolhido.emit(caminho)
        return card

    # ---------------- EVENTOS ----------------

    def _on_novo_projeto_clicked(self):
        self.fluxo_escolhido.emit(FLUXO_CADASTRO)

    def _on_projeto_double_clicked(self, item):
        caminho_projeto = item.data(QtCore.Qt.UserRole)
        self.projeto_selecionado.emit(caminho_projeto, "abrir")