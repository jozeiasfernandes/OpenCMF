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

    def __init__(self):
        super().__init__()
        self.base_dir = get_resource_path()
        self._lazy_registry: Dict[QtWidgets.QWidget, Dict[str, Any]] = {}

        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(False)

        self._setup_home_button()
        self.currentChanged.connect(self._on_tab_changed)

    def _setup_home_button(self):
        self.btn_home = HomeButton(self.base_dir, self.ICON_SIZE_HOME)
        self.btn_home.clicked_signal.connect(self.home_solicitada.emit)

        container = QtWidgets.QWidget()
        container.setFixedSize(50, self.TAB_HEIGHT)
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.addWidget(self.btn_home)
        self.setCornerWidget(container, QtCore.Qt.TopLeftCorner)

    def clear(self):
        self._lazy_registry.clear()
        while self.count() > 0:
            widget = self.widget(0)
            self.removeTab(0)
            if widget:
                widget.deleteLater()

    def adicionar_modulo(self, id_modulo: str, modulo_ref: Any, on_concluido=None):
        try:
            is_class = isinstance(modulo_ref, type)
            title = getattr(modulo_ref, 'nome', id_modulo.replace("_", " ").capitalize())
            container = QtWidgets.QWidget()

            self.blockSignals(True)
            self.addTab(container, title)
            self.blockSignals(False)

            if is_class:
                self._lazy_registry[container] = {
                    "id": id_modulo,
                    "classe": modulo_ref,
                    "instancia": None,
                    "carregado": False,
                    "container": container,
                    "on_concluido": on_concluido
                }
            else:
                container.setProperty("modulo_instancia", modulo_ref)
                if on_concluido and hasattr(modulo_ref, "concluido"):
                    modulo_ref.concluido.connect(on_concluido)
                self._build_module_layout(container, modulo_ref)

            if self.count() == 1:
                self.setCurrentIndex(0)
                self._on_tab_changed(0)

        except Exception as e:
            logger.error(f"Erro ao adicionar modulo {id_modulo}: {e}")
            logger.error(traceback.format_exc())

    def get_modulo_ativo(self) -> Optional[Any]:
        current = self.currentWidget()
        if not current:
            return None

        modulo = current.property("modulo_instancia")
        if not modulo and current in self._lazy_registry:
            data = self._lazy_registry[current]
            if not data["carregado"]:
                self._load_lazy_module(data)
            modulo = data["instancia"]
        return modulo

    def _on_tab_changed(self, index: int):
        container = self.widget(index)
        if data := self._lazy_registry.get(container):
            if not data["carregado"]:
                self._load_lazy_module(data)
        self._sync_active_view()

    def _load_lazy_module(self, data: Dict):
        try:
            instancia = data["classe"]()
            data["instancia"] = instancia
            data["container"].setProperty("modulo_instancia", instancia)

            if data["on_concluido"] and hasattr(instancia, "concluido"):
                instancia.concluido.connect(data["on_concluido"])

            self._build_module_layout(data["container"], instancia)
            data["carregado"] = True
        except Exception:
            logger.error(traceback.format_exc())

    def _sync_active_view(self):
        if modulo := self.get_modulo_ativo():
            QtCore.QTimer.singleShot(10, lambda: self._refresh_viewer(modulo))

    def _refresh_viewer(self, modulo: Any):
        viewer = getattr(modulo, 'viewer', None)
        if hasattr(viewer, 'refresh_display'):
            viewer.refresh_display()

    def _build_module_layout(self, container: QtWidgets.QWidget, modulo: Any):
        if container.layout():
            return

        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setHandleWidth(1)

        center = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        if hasattr(modulo, "get_workspace_toolbar") and (tb := modulo.get_workspace_toolbar()):
            center_layout.addWidget(tb)

        if hasattr(modulo, "get_workspace") and (vw := modulo.get_workspace()):
            vw.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            center_layout.addWidget(vw)

        splitter.addWidget(center)
        self._attach_sidebar(splitter, container, modulo)
        layout.addWidget(splitter)

    def _attach_sidebar(self, splitter: QtWidgets.QSplitter, container: QtWidgets.QWidget, modulo: Any):
        if not hasattr(modulo, 'get_toolboxes') or not (toolboxes := modulo.get_toolboxes()):
            return

        sidebar = QtWidgets.QTabWidget()
        sidebar.setTabPosition(QtWidgets.QTabWidget.East)
        sidebar.setMinimumWidth(self.SIDEBAR_COLLAPSED_WIDTH)
        sidebar.setMaximumWidth(self.SIDEBAR_COLLAPSED_WIDTH)

        for label, widget in toolboxes.items():
            wrapper = QtWidgets.QWidget()
            w_layout = QtWidgets.QVBoxLayout(wrapper)
            w_layout.setContentsMargins(0, 0, 0, 0)
            w_layout.addWidget(widget)
            sidebar.addTab(wrapper, label)
            wrapper.setVisible(False)

        sidebar.tabBarClicked.connect(partial(self._handle_sidebar, sidebar))
        splitter.addWidget(sidebar)
        splitter.setStretchFactor(0, 1)
        splitter.setSizes([container.width(), self.SIDEBAR_COLLAPSED_WIDTH])

    def _handle_sidebar(self, sidebar: QtWidgets.QTabWidget, index: int):
        is_expanded = sidebar.width() > self.SIDEBAR_COLLAPSED_WIDTH

        if is_expanded and index == sidebar.currentIndex():
            sidebar.setMaximumWidth(self.SIDEBAR_COLLAPSED_WIDTH)
            self._toggle_sidebar_widgets(sidebar, False)
        else:
            sidebar.setMaximumWidth(16777215)
            self._toggle_sidebar_widgets(sidebar, True)
            sidebar.setCurrentIndex(index)
            if splitter := sidebar.parentWidget().findChild(QtWidgets.QSplitter):
                new_width = splitter.width() - self.SIDEBAR_EXPANDED_WIDTH
                splitter.setSizes([new_width, self.SIDEBAR_EXPANDED_WIDTH])
        self._sync_active_view()

    def _toggle_sidebar_widgets(self, sidebar: QtWidgets.QTabWidget, visible: bool):
        for i in range(sidebar.count()):
            sidebar.widget(i).setVisible(visible)