from functools import partial
from pathlib import Path
from typing import Optional, Any, Dict
from PySide6 import QtWidgets, QtCore, QtGui


class WorkspaceManager(QtWidgets.QTabWidget):
    home_solicitada = QtCore.Signal()

    TOOLBOX_MIN_WIDTH = 35
    TOOLBOX_MAX_WIDTH = 250
    HOME_ICON_SIZE = QtCore.QSize(30, 30)
    HOME_BTN_SIZE = QtCore.QSize(30, 30)

    def __init__(self):
        super().__init__()
        self._config_estilo_abas()
        self._botao_home()
        self.currentChanged.connect(self._sincronizar_aba)

    def _config_estilo_abas(self):
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(False)

    def _botao_home(self):
        self.btn_home = QtWidgets.QToolButton()
        self.btn_home.setObjectName("botaoHomeWorkspace")
        self.btn_home.setFixedSize(self.HOME_BTN_SIZE)
        self.btn_home.setCursor(QtCore.Qt.PointingHandCursor)

        raiz = Path(__file__).parent.parent
        caminho_icone = raiz / "icones" / "home.png"
        if caminho_icone.exists():
            self.btn_home.setIcon(QtGui.QIcon(str(caminho_icone)))
            self.btn_home.setIconSize(self.HOME_ICON_SIZE)

        self.btn_home.clicked.connect(self.home_solicitada.emit)
        self.setCornerWidget(self.btn_home, QtCore.Qt.TopLeftCorner)

    def adicionar_modulo(self, id_modulo: str, modulo_obj: Any):
        titulo = getattr(modulo_obj, 'nome', id_modulo.replace("_", " ").capitalize())

        # 1. Criamos o container da página PRIMEIRO
        page_container = QtWidgets.QWidget()
        page_container.setProperty("modulo_instancia", modulo_obj)

        # 2. Adicionamos a aba antes de preencher o conteúdo.
        # Isso garante que qualquer widget criado pelo módulo já tenha um 'Parent' (a aba).
        self.blockSignals(True)
        idx = self.addTab(page_container, titulo)
        self.blockSignals(False)

        # 3. Agora preenchemos o layout com os componentes do módulo
        self._preencher_container_modulo(page_container, modulo_obj)

        if self.count() == 1:
            self.setCurrentIndex(0)

    def _preencher_container_modulo(self, page_container: QtWidgets.QWidget, modulo_obj: Any):
        layout_principal = QtWidgets.QHBoxLayout(page_container)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        centro_widget = QtWidgets.QWidget()
        centro_layout = QtWidgets.QVBoxLayout(centro_widget)
        centro_layout.setContentsMargins(0, 0, 0, 0)
        centro_layout.setSpacing(0)

        # Toolbar
        toolbar = modulo_obj.get_workspace_toolbar()
        if toolbar:
            centro_layout.addWidget(toolbar)

        # Solicita o Workspace (o main_container do módulo agora será filho de centro_widget)
        workspace_widget = modulo_obj.get_workspace()
        workspace_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        centro_layout.addWidget(workspace_widget)

        layout_principal.addWidget(centro_widget, stretch=1)

        # Sidebars (Toolboxes)
        if hasattr(modulo_obj, 'get_toolboxes'):
            dict_toolboxes = modulo_obj.get_toolboxes()
            if dict_toolboxes:
                sidebar = self._sidebar_lateral(dict_toolboxes)
                layout_principal.addWidget(sidebar)

    def get_modulo_ativo(self) -> Optional[Any]:
        container = self.currentWidget()
        return container.property("modulo_instancia") if container else None

    def _sidebar_lateral(self, toolboxes: Dict[str, QtWidgets.QWidget]) -> QtWidgets.QTabWidget:
        sidebar = QtWidgets.QTabWidget()
        sidebar.setTabPosition(QtWidgets.QTabWidget.East)
        sidebar.setFixedWidth(self.TOOLBOX_MIN_WIDTH)

        for nome_aba, widget_aba in toolboxes.items():
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.addWidget(widget_aba)
            sidebar.addTab(container, nome_aba)
            container.setVisible(False)

        sidebar.tabBarClicked.connect(partial(self._alternar_sidebar, sidebar))
        return sidebar

    def _alternar_sidebar(self, sidebar: QtWidgets.QTabWidget, index: int):
        largura_atual = sidebar.width()
        aba_atual = sidebar.currentIndex()

        if largura_atual <= self.TOOLBOX_MIN_WIDTH or index != aba_atual:
            sidebar.setFixedWidth(self.TOOLBOX_MAX_WIDTH + self.TOOLBOX_MIN_WIDTH)
            for i in range(sidebar.count()):
                sidebar.widget(i).setVisible(True)
        else:
            sidebar.setFixedWidth(self.TOOLBOX_MIN_WIDTH)
            for i in range(sidebar.count()):
                sidebar.widget(i).setVisible(False)

        modulo = self.get_modulo_ativo()
        if modulo:
            QtCore.QTimer.singleShot(10, lambda: self._refresh_visual(modulo))

        self.updateGeometry()

    def _refresh_visual(self, modulo_obj: Any):
        viewer = getattr(modulo_obj, 'viewer', None)
        if viewer and hasattr(viewer, 'refresh_display'):
            viewer.refresh_display()

    def _sincronizar_aba(self, index: int):
        modulo_obj = self.get_modulo_ativo()
        if modulo_obj:
            QtCore.QTimer.singleShot(2, lambda: self._refresh_visual(modulo_obj))