from functools import partial
from pathlib import Path
from typing import Optional, Any, Dict
from PySide6 import QtWidgets, QtCore, QtGui


class WorkspaceManager(QtWidgets.QTabWidget):
    home_solicitada = QtCore.Signal()

    # Largura da alça (abas) e largura total quando expandido
    TOOLBOX_MIN_WIDTH = 35
    TOOLBOX_MAX_WIDTH = 250
    HOME_ICON_SIZE = QtCore.QSize(30, 30)
    HOME_BTN_SIZE = QtCore.QSize(30, 30)

    def __init__(self):
        super().__init__()
        self._configurar_estilo_abas_principais()
        self._criar_botao_home()

    def _configurar_estilo_abas_principais(self):
        """Configura as abas horizontais superiores (os módulos)"""
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(False)

    def _criar_botao_home(self):
        self.btn_home = QtWidgets.QToolButton()
        self.btn_home.setObjectName("botaoHomeWorkspace")
        self.btn_home.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_home.setFixedSize(self.HOME_BTN_SIZE)

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
        titulo = getattr(modulo_obj, 'nome', id_modulo.replace("_", " ").capitalize())
        container = self._montar_container_modulo(modulo_obj)
        self.addTab(container, titulo)

    def _montar_container_modulo(self, modulo_obj: Any) -> QtWidgets.QWidget:
        page_container = QtWidgets.QWidget()
        page_container.setProperty("modulo_instancia", modulo_obj)

        layout_principal = QtWidgets.QHBoxLayout(page_container)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # --- ÁREA CENTRAL (Visualizadores) ---
        centro_widget = QtWidgets.QWidget()
        centro_layout = QtWidgets.QVBoxLayout(centro_widget)
        centro_layout.setContentsMargins(0, 0, 0, 0)
        centro_layout.setSpacing(0)

        toolbar = modulo_obj.get_workspace_toolbar()
        if toolbar:
            centro_layout.addWidget(toolbar)

        workspace_widget = modulo_obj.get_workspace()
        workspace_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        centro_layout.addWidget(workspace_widget)

        layout_principal.addWidget(centro_widget, stretch=1)

        # --- SIDEBAR DIREITA (Multi-abas Verticais) ---
        # Verificamos se o módulo tem o método get_toolboxes (plural)
        if hasattr(modulo_obj, 'get_toolboxes'):
            dict_toolboxes = modulo_obj.get_toolboxes()
            if dict_toolboxes:
                sidebar = self._criar_sidebar_multi_abas(dict_toolboxes)
                layout_principal.addWidget(sidebar)

        return page_container

    def _criar_sidebar_multi_abas(self, toolboxes: Dict[str, QtWidgets.QWidget]) -> QtWidgets.QTabWidget:
        """
        Cria o QTabWidget lateral com posição EAST.
        Cada item do dicionário vira uma aba vertical.
        """
        sidebar = QtWidgets.QTabWidget()
        sidebar.setTabPosition(QtWidgets.QTabWidget.East)

        # Define a largura inicial apenas para as abas (fechado)
        sidebar.setFixedWidth(self.TOOLBOX_MIN_WIDTH)

        # Adiciona as abas enviadas pelo módulo
        for nome_aba, widget_aba in toolboxes.items():
            # Adicionamos o widget dentro de um container com layout para garantir
            # que botões e labels respeitem o espaço
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.addWidget(widget_aba)

            sidebar.addTab(container, nome_aba)
            # Inicialmente escondemos o conteúdo para a barra parecer "fechada"
            container.setVisible(False)

        # Conecta o clique na aba para expandir/recolher
        sidebar.tabBarClicked.connect(partial(self._alternar_sidebar, sidebar))

        return sidebar

    def _alternar_sidebar(self, sidebar: QtWidgets.QTabWidget, index: int):
        """
        Lógica de expansão: se clicar na aba já ativa, ela fecha.
        Se clicar em uma nova ou se estiver fechada, ela abre.
        """
        largura_atual = sidebar.width()
        aba_atual = sidebar.currentIndex()

        # Se estiver fechado OU clicou em uma aba diferente da atual: ABRE
        if largura_atual <= self.TOOLBOX_MIN_WIDTH or index != aba_atual:
            sidebar.setFixedWidth(self.TOOLBOX_MAX_WIDTH + self.TOOLBOX_MIN_WIDTH)
            for i in range(sidebar.count()):
                sidebar.widget(i).setVisible(True)
        else:
            # Se clicou na mesma aba e já estava aberto: FECHA
            sidebar.setFixedWidth(self.TOOLBOX_MIN_WIDTH)
            for i in range(sidebar.count()):
                sidebar.widget(i).setVisible(False)

        self.updateGeometry()

