from PySide6 import QtWidgets, QtCore
from core.base_module.base import ModuloBase


class ModuloTemplate(ModuloBase):

    def __init__(self):
        super().__init__()
        self._is_initialized = False

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self._is_initialized = True

    def get_workspace(self) -> QtWidgets.QWidget:
        # Container principal que agrupa Toolbar Superior + Área de Visualização
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Adiciona a barra de ferramentas no topo
        layout.addWidget(self.get_workspace_toolbar())

        # Área de conteúdo (Ex: visualizador 3D)
        view_area = QtWidgets.QFrame()
        view_area.setStyleSheet("background-color: #1e1e1e;")  # Fundo escuro para contraste

        layout.addWidget(view_area, stretch=1)
        return container

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        # Barra de ferramentas horizontal que fica acima do Workspace
        toolbar = QtWidgets.QToolBar("Ferramentas de Visualização")
        toolbar.setIconSize(QtCore.QSize(24, 24))
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # Exemplo de ações comuns
        action_reset = toolbar.addAction("Resetar Visão")
        action_reset.setToolTip("Centralizar câmera")

        toolbar.addSeparator()

        action_screenshot = toolbar.addAction("Capturar Tela")
        action_screenshot.setToolTip("Salvar imagem do planejamento")

        return toolbar

    def get_toolbox(self) -> QtWidgets.QWidget:
        # Painel lateral para parâmetros e formulários
        toolbox = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(toolbox)

        layout.addWidget(QtWidgets.QLabel("<b>PARÂMETROS</b>"))
        layout.addWidget(QtWidgets.QPushButton("Executar Cálculo"))

        btn_concluir = QtWidgets.QPushButton("Finalizar Etapa")
        btn_concluir.setStyleSheet("font-weight: bold;")
        btn_concluir.clicked.connect(self._on_conclude_clicked)

        layout.addStretch()
        layout.addWidget(btn_concluir)

        return toolbox

