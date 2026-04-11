from functools import partial
from PySide6 import QtWidgets, QtCore, QtGui


class WorkspaceManager(QtWidgets.QTabWidget):
    home_solicitada = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self._configurar_visual()
        self._inicializar_interface()

    def _configurar_visual(self):
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(False)
        self.TOOLBOX_MIN = 35  # Aumentado levemente para não cortar o ícone
        self.TOOLBOX_MAX = 300
        self.ICONE_HOME = "icones/home.png"

    def _inicializar_interface(self):
        self.btn_home = QtWidgets.QToolButton()
        self.btn_home.setObjectName("botaoHomeWorkspace")
        self.btn_home.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_home.setFixedSize(32, 32)

        # Fallback caso o ícone não exista
        if QtGui.QPixmap(self.ICONE_HOME).isNull():
            self.btn_home.setText("H")
        else:
            self.btn_home.setIcon(QtGui.QIcon(self.ICONE_HOME))
            self.btn_home.setIconSize(QtCore.QSize(20, 20))

        self.btn_home.clicked.connect(self.home_solicitada.emit)
        self.setCornerWidget(self.btn_home, QtCore.Qt.TopLeftCorner)

    def get_modulo_ativo(self):
        container_atual = self.currentWidget()
        if container_atual:
            # Retorna a instância da classe Modulo guardada na propriedade
            return container_atual.property("modulo_instancia")
        return None

    def adicionar_modulo(self, id_modulo, modulo):
        # Evita nomes de abas vazios ou estranhos
        titulo = id_modulo.replace("_", " ").capitalize()
        container = self._criar_container_modulo(modulo)
        self.addTab(container, titulo)

    def _criar_container_modulo(self, modulo):
        widget = QtWidgets.QWidget()
        widget.setProperty("modulo_instancia", modulo)

        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # O segredo: Pegar o widget de interface do módulo
        interface_modulo = modulo.get_workspace()

        # IMPORTANTE: Forçar o widget a ocupar o máximo de espaço possível
        interface_modulo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        layout.addWidget(interface_modulo, stretch=1)

        # Sidebar de Ferramentas
        toolbox_widget = modulo.get_toolbox()
        sidebar = self._montar_sidebar(toolbox_widget)
        layout.addWidget(sidebar)

        return widget

    def avancar_aba(self) -> bool:
        proximo_indice = self.currentIndex() + 1
        if proximo_indice < self.count():
            self.setCurrentIndex(proximo_indice)
            return True
        return False

    def _montar_sidebar(self, widget_ferramentas):
        sidebar = QtWidgets.QTabWidget()
        sidebar.setTabPosition(QtWidgets.QTabWidget.East)
        sidebar.setFixedWidth(self.TOOLBOX_MIN)

        # Garante que o widget de ferramentas não inicie invisível internamente
        widget_ferramentas.setMinimumWidth(self.TOOLBOX_MAX - 40)

        # Adiciona a aba de Ferramentas
        sidebar.addTab(widget_ferramentas, "Ferramentas")

        # Começa com o conteúdo interno escondido
        widget_ferramentas.setVisible(False)

        sidebar.tabBarClicked.connect(partial(self._alternar_sidebar, sidebar))
        return sidebar

    def _alternar_sidebar(self, sidebar, indice):
        conteudo = sidebar.widget(indice)

        # Lógica de toggle (Abrir/Fechar)
        if sidebar.width() <= self.TOOLBOX_MIN:
            # Está fechado, vamos abrir
            sidebar.setFixedWidth(self.TOOLBOX_MAX)
            conteudo.setVisible(True)
        else:
            # Está aberto, vamos fechar
            sidebar.setFixedWidth(self.TOOLBOX_MIN)
            conteudo.setVisible(False)

        # Força o layout da janela a se reajustar
        self.updateGeometry()