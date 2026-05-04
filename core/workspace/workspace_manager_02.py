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
        def __init__(self, base_dir, size):
            super().__init__()
            self.setIconSize(size)
            self.setFixedSize(size)
            self.setCursor(QtCore.Qt.PointingHandCursor)
            self.setStyleSheet("QPushButton { border: none; background: transparent; padding: 2px; }")

            icon_path = base_dir / "appearance" / "icons" / "home.svg"
            if icon_path.exists():
                self.setIcon(QtGui.QIcon(str(icon_path)))
            else:
                self.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirHomeIcon))


def get_resource_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


class WorkspaceManager(QtWidgets.QWidget):
    home_solicitada = QtCore.Signal()
    config_solicitada = QtCore.Signal()
    currentChanged = QtCore.Signal(int)

    SIDEBAR_EXPANDED_WIDTH = 330
    DEBUG_TOOLBAR = "background-color: rgba(0,120,255,80);"
    DEBUG_CENTER = "background-color: rgba(0,200,0,80);"
    DEBUG_TOOLBOX = "background-color: rgba(255,80,80,80);"

    def __init__(self):
        super().__init__()
        self.base_dir = get_resource_path()
        self._lazy_registry: Dict[QtWidgets.QWidget, Dict[str, Any]] = {}

        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        self.header = QtWidgets.QWidget()
        self.header.setFixedHeight(45)
        self.header.setStyleSheet("background-color: #252525; border-bottom: 1px solid #333;")

        self.header_grid = QtWidgets.QGridLayout(self.header)
        self.header_grid.setContentsMargins(5, 0, 5, 0)
        self.header_grid.setSpacing(0)

        h_dim = 40
        icon_sz = QtCore.QSize(int(h_dim * 0.7), int(h_dim * 0.7))
        self.btn_home = HomeButton(self.base_dir, icon_sz)
        self.btn_home.clicked.connect(self.home_solicitada.emit)
        self.header_grid.addWidget(self.btn_home, 0, 0)

        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setMovable(False)
        self.tab_bar.setStyleSheet("""
            QTabBar::tab {
                background: #252525;
                color: #888;
                padding: 12px 20px;
                min-width: 100px;
                border-right: 1px solid #333;
            }
            QTabBar::tab:selected {
                background: #333;
                color: white;
                border-bottom: 2px solid #0078d7;
            }
        """)
        self.header_grid.addWidget(self.tab_bar, 0, 1)
        self.header_grid.setColumnStretch(2, 1)

        self.tab_bar.currentChanged.connect(self.currentChanged.emit)

        self.btn_config = QtWidgets.QPushButton()
        self.btn_config.setFixedSize(h_dim, h_dim)
        self.btn_config.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_config.setStyleSheet(
            "QPushButton { border: none; background: transparent; } QPushButton:hover { background-color: #444; }")

        icon_path = self.base_dir / "appearance" / "icons" / "config_branco.svg"
        if icon_path.exists():
            self.btn_config.setIcon(QtGui.QIcon(str(icon_path)))
        else:
            self.btn_config.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))

        self.btn_config.clicked.connect(self.config_solicitada.emit)
        self.header_grid.addWidget(self.btn_config, 0, 3)

        self.container_paginas = QtWidgets.QStackedWidget()
        self.layout_principal.addWidget(self.header)
        self.layout_principal.addWidget(self.container_paginas)

        self.tab_bar.currentChanged.connect(self._on_tab_changed)

    def count(self):
        return self.tab_bar.count()

    def clear(self):
        while self.tab_bar.count() > 0:
            self.tab_bar.removeTab(0)

        while self.container_paginas.count() > 0:
            widget = self.container_paginas.widget(0)
            if widget:
                self.container_paginas.removeWidget(widget)
                widget.deleteLater()

        self._lazy_registry.clear()

    def adicionar_modulo(self, id_modulo: str, modulo_ref: Any, on_concluido=None):
        try:
            is_class = isinstance(modulo_ref, type)
            title = getattr(modulo_ref, 'nome', id_modulo.replace("_", " ").capitalize())
            container = QtWidgets.QWidget()

            # Adiciona a aba e o widget
            idx = self.tab_bar.addTab(title)
            self.container_paginas.addWidget(container)

            if is_class:
                self._lazy_registry[container] = {
                    "id": id_modulo, "classe": modulo_ref, "instancia": None,
                    "carregado": False, "container": container, "on_concluido": on_concluido
                }
            else:
                container.setProperty("modulo_instancia", modulo_ref)
                self._build_module_layout(container, modulo_ref)

            # --- CORREÇÃO AQUI ---
            if self.tab_bar.count() == 1:
                self.tab_bar.setCurrentIndex(0)
                # Força o disparo manual para o primeiro módulo
                self._on_tab_changed(0)
                # ---------------------

        except Exception as e:
            logger.error(f"Erro ao adicionar modulo {id_modulo}: {e}")

    def _on_tab_changed(self, index: int):
        if index < 0: return
        self.container_paginas.setCurrentIndex(index)
        container = self.container_paginas.widget(index)
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

    def get_modulo_ativo(self) -> Optional[Any]:
        current = self.container_paginas.currentWidget()
        if not current: return None
        modulo = current.property("modulo_instancia")
        if not modulo and current in self._lazy_registry:
            return self._lazy_registry[current].get("instancia")
        return modulo

    def _build_module_layout(self, container: QtWidgets.QWidget, modulo: Any):
        if container.layout(): return
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setHandleWidth(1)
        center = QtWidgets.QWidget()
        center.setStyleSheet(self.DEBUG_CENTER)
        center_layout = QtWidgets.QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        if hasattr(modulo, "get_workspace_toolbar") and (tb := modulo.get_workspace_toolbar()):
            tb.setStyleSheet(self.DEBUG_TOOLBAR)
            center_layout.addWidget(tb)
        if hasattr(modulo, "get_workspace") and (vw := modulo.get_workspace()):
            vw.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            center_layout.addWidget(vw)
        splitter.addWidget(center)
        self._attach_sidebar(splitter, modulo)
        layout.addWidget(splitter)

    def _attach_sidebar(self, splitter: QtWidgets.QSplitter, modulo: Any):
        if not hasattr(modulo, 'get_toolboxes'): return
        toolboxes = modulo.get_toolboxes()
        if not toolboxes: return
        sidebar = QtWidgets.QWidget()
        sidebar_layout = QtWidgets.QHBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        stack = QtWidgets.QStackedWidget()
        stack.setFixedWidth(self.SIDEBAR_EXPANDED_WIDTH)
        stack.setStyleSheet(self.DEBUG_TOOLBOX)
        stack.hide()
        tab_bar_container = QtWidgets.QWidget()
        tab_bar_lyt = QtWidgets.QVBoxLayout(tab_bar_container)
        tab_bar_lyt.setContentsMargins(0, 0, 0, 0)
        tab_bar_lyt.setSpacing(0)
        tab_bar_side = QtWidgets.QTabBar()
        tab_bar_side.setShape(QtWidgets.QTabBar.RoundedEast)
        tab_bar_side.setCursor(QtCore.Qt.PointingHandCursor)
        for label, widget in toolboxes.items():
            tab_bar_side.addTab(label)
            stack.addWidget(widget)
        tab_bar_side.tabBarClicked.connect(partial(self._toggle_sidebar, stack, tab_bar_side))
        tab_bar_lyt.addWidget(tab_bar_side)
        tab_bar_lyt.addStretch()
        sidebar_layout.addWidget(stack)
        sidebar_layout.addWidget(tab_bar_container)
        splitter.addWidget(sidebar)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

    def _toggle_sidebar(self, stack, bar, index):
        if not stack.isHidden() and bar.currentIndex() == index:
            stack.hide()
            bar.setCurrentIndex(-1)
        else:
            stack.show()
            stack.setCurrentIndex(index)
        self._sync_active_view()

    def _sync_active_view(self):
        if modulo := self.get_modulo_ativo():
            QtCore.QTimer.singleShot(10, lambda: self._refresh_viewer(modulo))

    def _refresh_viewer(self, modulo: Any):
        viewer = getattr(modulo, 'viewer', None)
        if hasattr(viewer, 'refresh_display'):
            viewer.refresh_display()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    workspace = WorkspaceManager()


    class ModuloTeste:
        nome = "Pacientes"

        def get_workspace_toolbar(self):
            tb = QtWidgets.QToolBar();
            tb.addAction("Novo");
            return tb

        def get_workspace(self):
            return QtWidgets.QLabel("Área Central OpenCMF")

        def get_toolboxes(self):
            return {"Ferramentas": QtWidgets.QLabel("Painel Lateral")}


    workspace.adicionar_modulo("pacientes", ModuloTeste())
    workspace.resize(1000, 600)
    workspace.show()
    sys.exit(app.exec())