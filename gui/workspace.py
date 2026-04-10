from PySide6 import QtWidgets, QtCore
from functools import partial


class WorkspaceManager(QtWidgets.QTabWidget):
    home_solicitada = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self._configurar_layout()
        self._criar_botao_home()

    def _configurar_layout(self):
        self.setDocumentMode(True)
        self.TOOLBOX_MIN = 32
        self.TOOLBOX_MAX = 350

    def _criar_botao_home(self):
        self.btn_home = QtWidgets.QToolButton()
        self.btn_home.setObjectName("botaoHomeWorkspace")
        self.btn_home.setText("🏠")
        self.btn_home.setCursor(QtCore.Qt.PointingHandCursor)

        # O tamanho deve ser próximo à altura da barra de abas (geralmente 28-32px)
        self.btn_home.setFixedSize(32, 32)
        self.btn_home.clicked.connect(self.home_solicitada.emit)

        self.setCornerWidget(self.btn_home, QtCore.Qt.TopLeftCorner)

    def adicionar_modulo(self, id_modulo, modulo):
        conteudo_aba = self._montar_container_modulo(modulo)
        titulo = id_modulo.split('_')[-1].capitalize()
        self.addTab(conteudo_aba, titulo)

    def _montar_container_modulo(self, modulo):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(modulo.get_workspace(), stretch=1)

        toolbox = self._criar_painel_lateral(modulo.get_toolbox())
        layout.addWidget(toolbox)

        return container

    def _criar_painel_lateral(self, widget_ferramentas):
        toolbox = QtWidgets.QTabWidget()
        toolbox.setTabPosition(QtWidgets.QTabWidget.East)
        toolbox.setFixedWidth(self.TOOLBOX_MIN)

        widget_ferramentas.setVisible(False)
        toolbox.addTab(widget_ferramentas, "Ferramentas")

        callback = partial(self._gerenciar_painel_lateral, toolbox)
        toolbox.tabBarClicked.connect(callback)

        return toolbox

    def _gerenciar_painel_lateral(self, toolbox, indice):
        widget = toolbox.widget(indice)

        if toolbox.currentIndex() == indice:
            novo_estado = not widget.isVisible()
            widget.setVisible(novo_estado)
            toolbox.setFixedWidth(self.TOOLBOX_MAX if novo_estado else self.TOOLBOX_MIN)
        else:
            widget.setVisible(True)
            toolbox.setFixedWidth(self.TOOLBOX_MAX)