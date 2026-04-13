# WorkspaceManager.py

from functools import partial
from pathlib import Path
from typing import Optional, Any

from PySide6 import QtWidgets, QtCore, QtGui


class WorkspaceManager(QtWidgets.QTabWidget):
    home_solicitada = QtCore.Signal()

    TOOLBOX_MIN_WIDTH = 35
    TOOLBOX_MAX_WIDTH = 250
    HOME_ICON_SIZE = QtCore.QSize(30, 30)
    HOME_BTN_SIZE = QtCore.QSize(30, 30)

    def __init__(self):
        super().__init__()
        self._configurar_estilo_abas()
        self._criar_botao_home()

    def _configurar_estilo_abas(self):
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(False)

    def _criar_botao_home(self):
        self.btn_home = QtWidgets.QToolButton()
        self.btn_home.setObjectName("botaoHomeWorkspace")
        self.btn_home.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_home.setFixedSize(self.HOME_BTN_SIZE)

        # Caminho relativo corrigido para a estrutura da raiz
        raiz = Path(__file__).parent.parent
        caminho_icone = raiz / "icones" / "home.png"

        if caminho_icone.exists():
            self.btn_home.setIcon(QtGui.QIcon(str(caminho_icone)))
            self.btn_home.setIconSize(self.HOME_ICON_SIZE)
        else:
            self.btn_home.setText("H")

        self.btn_home.clicked.connect(self.home_solicitada.emit)
        self.setCornerWidget(self.btn_home, QtCore.Qt.TopLeftCorner)

    def get_modulo_ativo(self) -> Optional[Any]:
        container = self.currentWidget()
        return container.property("modulo_instancia") if container else None

    def adicionar_modulo(self, id_modulo: str, modulo_obj: Any):
        titulo = id_modulo.replace("_", " ").capitalize()
        container = self._montar_container_modulo(modulo_obj)
        self.addTab(container, titulo)

    def _montar_container_modulo(self, modulo_obj: Any) -> QtWidgets.QWidget:
        page_container = QtWidgets.QWidget()
        page_container.setProperty("modulo_instancia", modulo_obj)

        layout_principal = QtWidgets.QHBoxLayout(page_container)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        centro_widget = QtWidgets.QWidget()
        centro_layout = QtWidgets.QVBoxLayout(centro_widget)
        centro_layout.setContentsMargins(0, 0, 0, 0)
        centro_layout.setSpacing(0)

        toolbar = modulo_obj.get_workspace_toolbar()
        if toolbar:
            centro_layout.addWidget(toolbar)

        workspace_widget = modulo_obj.get_workspace()
        workspace_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        centro_layout.addWidget(workspace_widget)

        layout_principal.addWidget(centro_widget, stretch=1)

        toolbox_widget = modulo_obj.get_toolbox()
        if self._validar_toolbox(toolbox_widget):
            sidebar = self._criar_sidebar_retratil(toolbox_widget)
            layout_principal.addWidget(sidebar)

        return page_container

    def _validar_toolbox(self, widget: QtWidgets.QWidget) -> bool:
        if widget is None:
            return False
        if isinstance(widget, QtWidgets.QTabWidget):
            return widget.count() > 0
        if type(widget) == QtWidgets.QWidget and not widget.children():
            return False
        return True

    def _criar_sidebar_retratil(self, widget_ferramentas: QtWidgets.QWidget) -> QtWidgets.QTabWidget:
        # Define se usa o conjunto de abas do módulo ou cria um novo
        if isinstance(widget_ferramentas, QtWidgets.QTabWidget):
            sidebar = widget_ferramentas
        else:
            sidebar = QtWidgets.QTabWidget()
            sidebar.addTab(widget_ferramentas, "Ferramentas")

        sidebar.setTabPosition(QtWidgets.QTabWidget.East)
        sidebar.setFixedWidth(self.TOOLBOX_MIN_WIDTH)

        # Esconde o conteúdo inicial
        for i in range(sidebar.count()):
            w = sidebar.widget(i)
            if w:
                w.setHidden(True)

        # CORREÇÃO DO WARNING: Conecta apenas se ainda não houver conexão
        # O partial garante que passamos a sidebar correta para a função
        sidebar.tabBarClicked.connect(partial(self._alternar_sidebar, sidebar))

        return sidebar

    def _alternar_sidebar(self, sidebar: QtWidgets.QTabWidget, index: int):
        # Lógica de alternância baseada no estado atual da largura
        esta_aberta = sidebar.width() > self.TOOLBOX_MIN_WIDTH

        if not esta_aberta:
            sidebar.setFixedWidth(self.TOOLBOX_MAX_WIDTH)
            for i in range(sidebar.count()):
                w = sidebar.widget(i)
                if w:
                    w.setHidden(False)
        else:
            sidebar.setFixedWidth(self.TOOLBOX_MIN_WIDTH)
            for i in range(sidebar.count()):
                w = sidebar.widget(i)
                if w:
                    w.setHidden(True)

        self.updateGeometry()



        Teste