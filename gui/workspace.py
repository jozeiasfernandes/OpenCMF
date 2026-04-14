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
        self._configurar_estilo_abas_principais()
        self._criar_botao_home()

        # GATILHO: Sempre que a aba mudar (ex: entrar em Tomografia), dispara o refresh
        self.currentChanged.connect(self._ao_mudar_aba)

    def _ao_mudar_aba(self, index: int):
        """Gerencia o refresh automático quando o usuário entra no módulo."""
        modulo_obj = self.get_modulo_ativo()
        if modulo_obj:
            # Aguarda 50ms para o Qt terminar de desenhar a UI (toolbar/sidebar)
            # e então força o VTK a renderizar no espaço que sobrou.
            QtCore.QTimer.singleShot(50, lambda: self._refresh_workspace_modulo(modulo_obj))

    def _refresh_workspace_modulo(self, modulo_obj: Any):
        """Procura o viewer no módulo e solicita a atualização de tela."""
        # Tenta encontrar o viewer (VolumeViewerWidget) dentro do módulo
        viewer = getattr(modulo_obj, 'viewer', None)
        if viewer and hasattr(viewer, 'refresh_display'):
            print(f">>> [SISTEMA] Estabilizando workspace: {modulo_obj.nome}")
            viewer.refresh_display()

    # --- MÉTODOS EXISTENTES SEM ALTERAÇÃO ---

    def _configurar_estilo_abas_principais(self):
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(False)

    def _criar_botao_home(self):
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

    def get_modulo_ativo(self) -> Optional[Any]:
        container = self.currentWidget()
        return container.property("modulo_instancia") if container else None

    def adicionar_modulo(self, id_modulo: str, modulo_obj: Any):
        titulo = getattr(modulo_obj, 'nome', id_modulo.replace("_", " ").capitalize())
        container = self._montar_container_modulo(modulo_obj)

        # BLOQUEIA sinais temporariamente para não disparar o _ao_mudar_aba
        self.blockSignals(True)
        idx = self.addTab(container, titulo)
        self.blockSignals(False)

        # Opcional: Se você quiser que o primeiro módulo (Paciente) seja o padrão
        # Sem disparar o refresh de tomografia antes da hora
        if self.count() == 1:
            self.setCurrentIndex(0)

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
        if toolbar: centro_layout.addWidget(toolbar)

        workspace_widget = modulo_obj.get_workspace()
        workspace_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        centro_layout.addWidget(workspace_widget)

        layout_principal.addWidget(centro_widget, stretch=1)

        if hasattr(modulo_obj, 'get_toolboxes'):
            dict_toolboxes = modulo_obj.get_toolboxes()
            if dict_toolboxes:
                sidebar = self._criar_sidebar_multi_abas(dict_toolboxes)
                layout_principal.addWidget(sidebar)

        return page_container

    def _criar_sidebar_multi_abas(self, toolboxes: Dict[str, QtWidgets.QWidget]) -> QtWidgets.QTabWidget:
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

        # Importante: Após abrir/fechar a sidebar, as janelas VTK precisam de novo refresh!
        modulo = self.get_modulo_ativo()
        if modulo:
            QtCore.QTimer.singleShot(10, lambda: self._refresh_workspace_modulo(modulo))

        self.updateGeometry()

