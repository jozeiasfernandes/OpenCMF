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
        self.TOOLBOX_MIN = 32
        self.TOOLBOX_MAX = 350
        self.ICONE_HOME = "icones/home.png"

    def _inicializar_interface(self):
        self.btn_home = QtWidgets.QToolButton()
        self.btn_home.setObjectName("botaoHomeWorkspace")
        self.btn_home.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_home.setFixedSize(32, 32)

        # Ajuste de ícone com respiro visual (padding interno)
        self.btn_home.setIcon(QtGui.QIcon(self.ICONE_HOME))
        self.btn_home.setIconSize(QtCore.QSize(24, 24))

        self.btn_home.clicked.connect(self.home_solicitada.emit)
        self.setCornerWidget(self.btn_home, QtCore.Qt.TopLeftCorner)

    def adicionar_modulo(self, id_modulo, modulo):
        titulo = id_modulo.split('_')[-1].capitalize()
        container = self._criar_container_modulo(modulo)
        self.addTab(container, titulo)

    def _criar_container_modulo(self, modulo):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Adiciona área de trabalho do módulo e painel de ferramentas
        layout.addWidget(modulo.get_workspace(), stretch=1)
        layout.addWidget(self._montar_sidebar(modulo.get_toolbox()))

        return widget

    def _montar_sidebar(self, widget_ferramentas):
        sidebar = QtWidgets.QTabWidget()
        sidebar.setTabPosition(QtWidgets.QTabWidget.East)
        sidebar.setFixedWidth(self.TOOLBOX_MIN)

        widget_ferramentas.setVisible(False)
        sidebar.addTab(widget_ferramentas, "Ferramentas")

        sidebar.tabBarClicked.connect(partial(self._alternar_sidebar, sidebar))
        return sidebar

    def _alternar_sidebar(self, sidebar, indice):
        conteudo = sidebar.widget(indice)

        if sidebar.currentIndex() == indice:
            esta_visivel = not conteudo.isVisible()
            conteudo.setVisible(esta_visivel)
            largura = self.TOOLBOX_MAX if esta_visivel else self.TOOLBOX_MIN
            sidebar.setFixedWidth(largura)
        else:
            conteudo.setVisible(True)
            sidebar.setFixedWidth(self.TOOLBOX_MAX)