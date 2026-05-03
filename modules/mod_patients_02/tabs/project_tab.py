from pathlib import Path
from PySide6 import QtWidgets, QtCore


class ProjetosTab(QtWidgets.QWidget):
    projeto_aberto = QtCore.Signal(str)

    def __init__(self, project_manager=None):
        super().__init__()
        self.project_manager = project_manager
        self.pasta_paciente = None
        self._init_ui()
        self._build_layout()

    def _init_ui(self):
        self.lista_projetos = QtWidgets.QListWidget()
        self.lista_projetos.setSpacing(2)
        self.lista_projetos.itemDoubleClicked.connect(self._abrir_projeto)

        self.btn_novo_projeto = QtWidgets.QPushButton("Criar Novo Projeto")
        self.btn_novo_projeto.setMinimumHeight(45)
        self.btn_novo_projeto.clicked.connect(self._criar_projeto)

        self.btn_abrir = QtWidgets.QPushButton("Abrir Selecionado")
        self.btn_abrir.clicked.connect(self._abrir_projeto)

    def _build_layout(self):
        layout = QtWidgets.QVBoxLayout(self)

        botoes_layout = QtWidgets.QHBoxLayout()
        botoes_layout.addWidget(self.btn_novo_projeto)
        botoes_layout.addWidget(self.btn_abrir)

        layout.addWidget(QtWidgets.QLabel("Projetos do Paciente:"))
        layout.addWidget(self.lista_projetos)
        layout.addLayout(botoes_layout)

    def set_data(self, data: dict, pasta: str = None):
        if pasta:
            self.pasta_paciente = pasta
            self._atualizar_lista()

    def _atualizar_lista(self):
        self.lista_projetos.clear()
        if not self.pasta_paciente:
            return

        caminho_projetos = Path(self.pasta_paciente) / "projects"
        if not caminho_projetos.exists():
            return

        projetos = [p.name for p in caminho_projetos.iterdir() if p.is_dir()]
        self.lista_projetos.addItems(projetos)

    def _criar_projeto(self):
        if not self.pasta_paciente:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Identifique o paciente primeiro.")
            return

        nome, ok = QtWidgets.QInputDialog.getText(self, "Novo Projeto", "Nome do projeto:")
        if ok and nome:
            caminho = Path(self.pasta_paciente) / "projects" / nome
            try:
                caminho.mkdir(parents=True, exist_ok=True)
                self._atualizar_lista()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao criar pasta: {e}")

    def _abrir_projeto(self):
        item = self.lista_projetos.currentItem()
        if not item:
            return

        nome_projeto = item.text()
        caminho_completo = str(Path(self.pasta_paciente) / "projects" / nome_projeto)
        self.projeto_aberto.emit(caminho_completo)