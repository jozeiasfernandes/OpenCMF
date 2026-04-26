import sys
from functools import partial
from pathlib import Path
from typing import Optional, Any, Dict
from PySide6 import QtWidgets, QtCore, QtGui


def get_resource_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent


class WorkspaceManager(QtWidgets.QTabWidget):
    home_solicitada = QtCore.Signal()

    TOOLBOX_MIN_WIDTH = 35
    TOOLBOX_EXPAND_WIDTH = 330
    HOME_ICON_SIZE = QtCore.QSize(30, 30)
    HOME_BTN_SIZE = QtCore.QSize(30, 30)

    def __init__(self):
        super().__init__()
        self.base_dir = get_resource_path()
        self.init_interface()
        self.configurar_botao_home()
        self.currentChanged.connect(self.ao_mudar_aba)

    def init_interface(self):
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(False)

    def configurar_botao_home(self):
        self.btn_home = QtWidgets.QToolButton()
        self.btn_home.setObjectName("botaoHomeWorkspace")
        self.btn_home.setFixedSize(self.HOME_BTN_SIZE)
        self.btn_home.setCursor(QtCore.Qt.PointingHandCursor)

        caminho_icone = self.base_dir / "icons" / "home.png"
        if caminho_icone.exists():
            self.btn_home.setIcon(QtGui.QIcon(str(caminho_icone)))
            self.btn_home.setIconSize(self.HOME_ICON_SIZE)

        self.btn_home.clicked.connect(self.home_solicitada.emit)
        self.setCornerWidget(self.btn_home, QtCore.Qt.TopLeftCorner)

    def adicionar_modulo(self, id_modulo: str, modulo_obj: Any):
        titulo = getattr(modulo_obj, 'nome', id_modulo.replace("_", " ").capitalize())
        container = QtWidgets.QWidget()
        container.setProperty("modulo_instancia", modulo_obj)

        self.blockSignals(True)
        self.addTab(container, titulo)
        self.blockSignals(False)

        self.preencher_layout_modulo(container, modulo_obj)

        if self.count() == 1:
            self.setCurrentIndex(0)

    def preencher_layout_modulo(self, container: QtWidgets.QWidget, modulo_obj: Any):
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setObjectName("workspaceSplitter")
        splitter.setHandleWidth(1)

        centro = QtWidgets.QWidget()
        layout_centro = QtWidgets.QVBoxLayout(centro)
        layout_centro.setContentsMargins(0, 0, 0, 0)
        layout_centro.setSpacing(0)

        toolbar = modulo_obj.get_workspace_toolbar()
        if toolbar:
            layout_centro.addWidget(toolbar)

        view = modulo_obj.get_workspace()
        view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout_centro.addWidget(view)

        splitter.addWidget(centro)

        if hasattr(modulo_obj, 'get_toolboxes'):
            ferramentas = modulo_obj.get_toolboxes()
            if ferramentas:
                sidebar = self.criar_sidebar(ferramentas)
                splitter.addWidget(sidebar)
                splitter.setStretchFactor(0, 1)
                splitter.setStretchFactor(1, 0)
                splitter.setSizes([container.width(), self.TOOLBOX_MIN_WIDTH])

        layout.addWidget(splitter)

    def criar_sidebar(self, toolboxes: Dict[str, QtWidgets.QWidget]) -> QtWidgets.QTabWidget:
        sidebar = QtWidgets.QTabWidget()
        sidebar.setTabPosition(QtWidgets.QTabWidget.East)
        sidebar.setMinimumWidth(self.TOOLBOX_MIN_WIDTH)
        sidebar.setMaximumWidth(self.TOOLBOX_MIN_WIDTH)

        for nome, widget in toolboxes.items():
            aba = QtWidgets.QWidget()
            layout_aba = QtWidgets.QVBoxLayout(aba)
            layout_aba.setContentsMargins(0, 0, 0, 0)
            layout_aba.addWidget(widget)
            sidebar.addTab(aba, nome)
            aba.setVisible(False)

        sidebar.tabBarClicked.connect(partial(self.gerenciar_clique_sidebar, sidebar))
        return sidebar

    def gerenciar_clique_sidebar(self, sidebar: QtWidgets.QTabWidget, index: int):
        splitter = sidebar.parent()
        if not isinstance(splitter, QtWidgets.QSplitter):
            splitter = sidebar.parentWidget().findChild(QtWidgets.QSplitter)

        expandida = sidebar.width() > self.TOOLBOX_MIN_WIDTH
        aba_atual = sidebar.currentIndex()

        if expandida and index == aba_atual:
            sidebar.setMaximumWidth(self.TOOLBOX_MIN_WIDTH)
            for i in range(sidebar.count()):
                sidebar.widget(i).setVisible(False)
            if splitter:
                splitter.setSizes([10000, self.TOOLBOX_MIN_WIDTH])
        else:
            sidebar.setMaximumWidth(16777215)
            for i in range(sidebar.count()):
                sidebar.widget(i).setVisible(True)
            sidebar.setCurrentIndex(index)
            if splitter:
                largura_centro = splitter.width() - self.TOOLBOX_EXPAND_WIDTH
                splitter.setSizes([largura_centro, self.TOOLBOX_EXPAND_WIDTH])

        self.atualizar_visual_modulo_ativo()

    def get_modulo_ativo(self) -> Optional[Any]:
        container = self.currentWidget()
        return container.property("modulo_instancia") if container else None

    def atualizar_visual_modulo_ativo(self):
        modulo = self.get_modulo_ativo()
        if modulo:
            QtCore.QTimer.singleShot(10, lambda: self.forcar_refresh_viewer(modulo))

    def forcar_refresh_viewer(self, modulo_obj: Any):
        viewer = getattr(modulo_obj, 'viewer', None)
        if viewer and hasattr(viewer, 'refresh_display'):
            viewer.refresh_display()

    def ao_mudar_aba(self, index: int):
        self.atualizar_visual_modulo_ativo()