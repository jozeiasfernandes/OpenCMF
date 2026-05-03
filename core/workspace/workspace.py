import sys
import logging
import traceback
from functools import partial
from pathlib import Path
from typing import Optional, Any, Dict
from PySide6 import QtWidgets, QtCore, QtGui

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkspaceManager")

try:
    from .btn_home import HomeButton
except ImportError:
    class HomeButton(QtWidgets.QPushButton):
        def __init__(self, path, size):
            super().__init__()
            self.setIconSize(size)
            self.setFixedSize(size)
            self.setCursor(QtCore.Qt.PointingHandCursor)
            self.setStyleSheet("QPushButton { border: none; background: transparent; padding: 10px; }")
            self.clicked_signal = self.clicked


def get_resource_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent


class WorkspaceManager(QtWidgets.QTabWidget):
    home_solicitada = QtCore.Signal()
    SIDEBAR_COLLAPSED_WIDTH = 35
    SIDEBAR_EXPANDED_WIDTH = 330
    TAB_HEIGHT = 40
    ICON_SIZE_HOME = QtCore.QSize(40, 40)
    MAX_WIDGET_WIDTH = 16777215

    def __init__(self):
        super().__init__()
        logger.debug("Inicializando WorkspaceManager")
        self.base_dir = get_resource_path()
        self._configure_workspace_settings()
        self._setup_home_button()
        self.currentChanged.connect(self._on_tab_changed)

    def _configure_workspace_settings(self):
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(False)
        self.setStyleSheet(f"QTabBar::tab {{ height: {self.TAB_HEIGHT}px; }}")

    def _setup_home_button(self):
        self.btn_home = HomeButton(self.base_dir, self.ICON_SIZE_HOME)
        self.btn_home.clicked_signal.connect(self.home_solicitada.emit)
        container = QtWidgets.QWidget()
        container.setFixedSize(50, self.TAB_HEIGHT)
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.addWidget(self.btn_home)
        self.setCornerWidget(container, QtCore.Qt.TopLeftCorner)

    def adicionar_modulo(self, id_modulo: str, modulo_obj: Any):
        try:
            logger.info(f"Adicionando módulo: {id_modulo}")
            title = getattr(modulo_obj, 'nome', id_modulo.replace("_", " ").capitalize())
            container = self._create_module_container(modulo_obj)

            self.blockSignals(True)
            index = self.addTab(container, title)
            self.blockSignals(False)

            self._build_module_layout(container, modulo_obj)
            self._ensure_first_tab_active()
            logger.debug(f"Módulo {id_modulo} inserido no índice {index}")
        except Exception as e:
            logger.error(f"Erro ao adicionar módulo {id_modulo}: {e}")
            logger.error(traceback.format_exc())

    def _create_module_container(self, modulo_obj: Any) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        container.setProperty("modulo_instancia", modulo_obj)
        return container

    def _ensure_first_tab_active(self):
        if self.count() == 1:
            self.setCurrentIndex(0)

    def get_modulo_ativo(self) -> Optional[Any]:
        current_container = self.currentWidget()
        return current_container.property("modulo_instancia") if current_container else None

    def _on_tab_changed(self, index: int):
        modulo = self.get_modulo_ativo()
        nome = getattr(modulo, 'nome', 'Desconhecido') if modulo else 'Nenhum'
        logger.debug(f"Aba alterada para índice {index} (Módulo: {nome})")
        self._sync_active_module_view()

    def _sync_active_module_view(self):
        active_module = self.get_modulo_ativo()
        if active_module:
            QtCore.QTimer.singleShot(10, lambda: self._refresh_module_display(active_module))

    def _refresh_module_display(self, modulo_obj: Any):
        try:
            viewer = getattr(modulo_obj, 'viewer', None)
            if hasattr(viewer, 'refresh_display'):
                logger.debug("Solicitando refresh_display ao viewer do módulo")
                viewer.refresh_display()
        except Exception as e:
            logger.warning(f"Falha ao dar refresh no display: {e}")

    def _build_module_layout(self, container: QtWidgets.QWidget, modulo_obj: Any):
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        main_splitter = self._create_main_splitter()
        center_view = self._create_center_view(modulo_obj)
        main_splitter.addWidget(center_view)

        self._attach_sidebar_if_needed(main_splitter, container, modulo_obj)
        layout.addWidget(main_splitter)

    def _create_main_splitter(self) -> QtWidgets.QSplitter:
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setHandleWidth(1)
        return splitter

    def _create_center_view(self, modulo_obj: Any) -> QtWidgets.QWidget:
        center_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(center_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = modulo_obj.get_workspace_toolbar()
        if toolbar:
            layout.addWidget(toolbar)

        view = modulo_obj.get_workspace()
        if view:
            view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            layout.addWidget(view)
        return center_widget

    def _attach_sidebar_if_needed(self, splitter: QtWidgets.QSplitter, container: QtWidgets.QWidget, modulo_obj: Any):
        if not hasattr(modulo_obj, 'get_toolboxes'):
            return

        toolboxes = modulo_obj.get_toolboxes()
        if not toolboxes:
            return

        logger.debug(f"Anexando sidebar com {len(toolboxes)} toolboxes")
        sidebar = self._create_sidebar(toolboxes)
        splitter.addWidget(sidebar)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([container.width(), self.SIDEBAR_COLLAPSED_WIDTH])

    def _create_sidebar(self, toolboxes: Dict[str, QtWidgets.QWidget]) -> QtWidgets.QTabWidget:
        sidebar = QtWidgets.QTabWidget()
        sidebar.setTabPosition(QtWidgets.QTabWidget.East)
        sidebar.setMinimumWidth(self.SIDEBAR_COLLAPSED_WIDTH)
        sidebar.setMaximumWidth(self.SIDEBAR_COLLAPSED_WIDTH)

        for label, widget in toolboxes.items():
            tab_content = self._wrap_toolbox_widget(widget)
            sidebar.addTab(tab_content, label)
            tab_content.setVisible(False)

        sidebar.tabBarClicked.connect(partial(self._handle_sidebar_interaction, sidebar))
        return sidebar

    def _wrap_toolbox_widget(self, widget: QtWidgets.QWidget) -> QtWidgets.QWidget:
        wrapper = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        return wrapper

    def _handle_sidebar_interaction(self, sidebar: QtWidgets.QTabWidget, clicked_index: int):
        is_already_expanded = sidebar.width() > self.SIDEBAR_COLLAPSED_WIDTH
        is_same_tab = clicked_index == sidebar.currentIndex()

        if is_already_expanded and is_same_tab:
            logger.debug("Recolhendo sidebar")
            self._collapse_sidebar(sidebar)
        else:
            logger.debug(f"Expandindo sidebar na aba {clicked_index}")
            self._expand_sidebar(sidebar, clicked_index)
        self._sync_active_module_view()

    def _collapse_sidebar(self, sidebar: QtWidgets.QTabWidget):
        sidebar.setMaximumWidth(self.SIDEBAR_COLLAPSED_WIDTH)
        self._set_tabs_visibility(sidebar, False)
        splitter = self._find_parent_splitter(sidebar)
        if splitter:
            splitter.setSizes([10000, self.SIDEBAR_COLLAPSED_WIDTH])

    def _expand_sidebar(self, sidebar: QtWidgets.QTabWidget, index: int):
        sidebar.setMaximumWidth(self.MAX_WIDGET_WIDTH)
        self._set_tabs_visibility(sidebar, True)
        sidebar.setCurrentIndex(index)
        splitter = self._find_parent_splitter(sidebar)
        if splitter:
            available_width = splitter.width() - self.SIDEBAR_EXPANDED_WIDTH
            splitter.setSizes([available_width, self.SIDEBAR_EXPANDED_WIDTH])

    def _set_tabs_visibility(self, sidebar: QtWidgets.QTabWidget, visible: bool):
        for i in range(sidebar.count()):
            sidebar.widget(i).setVisible(visible)

    def _find_parent_splitter(self, widget: QtWidgets.QWidget) -> Optional[QtWidgets.QSplitter]:
        parent = widget.parent()
        if isinstance(parent, QtWidgets.QSplitter):
            return parent
        return widget.parentWidget().findChild(QtWidgets.QSplitter)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)


    class MockModulo:
        def __init__(self, nome, cor):
            self.nome = nome
            self.cor = cor

        def get_workspace_toolbar(self): return QtWidgets.QToolBar()

        def get_workspace(self):
            w = QtWidgets.QFrame()
            w.setStyleSheet(f"background-color: {self.cor};")
            return w

        def get_toolboxes(self): return {"Opções": QtWidgets.QLabel("Painel de Controle")}


    manager = WorkspaceManager()
    manager.adicionar_modulo("teste", MockModulo("Módulo Teste", "#34495e"))
    manager.resize(700, 500)
    manager.show()
    sys.exit(app.exec())