import sys
import logging
import traceback
from pathlib import Path
from typing import Optional, Any, Dict

from PySide6 import QtWidgets, QtCore, QtGui

from core.workspace.toolboxes_manager import ToolboxesManager
from core.workspace.loader_components import ComponentLoader
from core.workspace.componentes_list import Components_List

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkspaceManager")


def get_resource_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


class WorkspaceManager(QtWidgets.QWidget):
    home_solicitada = QtCore.Signal()
    config_solicitada = QtCore.Signal()
    currentChanged = QtCore.Signal(int)

    def __init__(self):
        super().__init__()
        self.base_dir = get_resource_path()
        self._lazy_registry: Dict[QtWidgets.QWidget, Dict[str, Any]] = {}
        self._config_window = None

        self._init_ui()

    def _init_ui(self):
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        self.header = QtWidgets.QWidget()
        self.header.setFixedHeight(45)
        header_grid = QtWidgets.QGridLayout(self.header)
        header_grid.setContentsMargins(5, 0, 5, 0)

        self.btn_home = QtWidgets.QPushButton()
        self.btn_home.setFixedSize(30, 30)
        self._apply_icon(self.btn_home, "home.svg", QtWidgets.QStyle.SP_DirHomeIcon)
        self.btn_home.clicked.connect(self.home_solicitada.emit)

        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.currentChanged.connect(self.currentChanged.emit)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        self.btn_config = QtWidgets.QPushButton()
        self.btn_config.setFixedSize(30, 30)
        self._apply_icon(self.btn_config, "config_branco.svg", QtWidgets.QStyle.SP_ComputerIcon)
        self.btn_config.clicked.connect(self._abrir_configuracoes)

        header_grid.addWidget(self.btn_home, 0, 0)
        header_grid.addWidget(self.tab_bar, 0, 1)
        header_grid.setColumnStretch(2, 1)
        header_grid.addWidget(self.btn_config, 0, 3)

        self.container_paginas = QtWidgets.QStackedWidget()
        self.layout_principal.addWidget(self.header)
        self.layout_principal.addWidget(self.container_paginas)

    def _apply_icon(self, button, name, fallback):
        path = self.base_dir / "appearance" / "icons" / name
        icon = QtGui.QIcon(str(path)) if path.exists() else self.style().standardIcon(fallback)
        button.setIcon(icon)
        button.setCursor(QtCore.Qt.PointingHandCursor)

    def _abrir_configuracoes(self):
        self.config_solicitada.emit()
        if not self._config_window:
            self._config_window = Components_List()
            self._config_window.componente_alterado.connect(self._on_componente_configurado)
        self._config_window.show()

    def clear(self):
        while self.tab_bar.count():
            self.tab_bar.removeTab(0)
        while self.container_paginas.count():
            w = self.container_paginas.widget(0)
            self.container_paginas.removeWidget(w)
            w.deleteLater()
        self._lazy_registry.clear()

    def adicionar_modulo(self, id_modulo: str, modulo_ref: Any, on_concluido=None):
        try:
            is_class = isinstance(modulo_ref, type)
            title = getattr(modulo_ref, 'nome', id_modulo.replace("_", " ").capitalize())

            container = QtWidgets.QWidget()
            self.tab_bar.addTab(title)
            self.container_paginas.addWidget(container)

            self._lazy_registry[container] = {
                "id": id_modulo,
                "classe": modulo_ref,
                "instancia": modulo_ref if not is_class else None,
                "carregado": not is_class,
                "on_concluido": on_concluido,
                "container": container,
                "sidebar": None,
                "layout_central": None
            }

            if not is_class:
                self._build_module_layout(container, modulo_ref)

            if self.tab_bar.count() == 1:
                self._on_tab_changed(0)

        except Exception:
            logger.error(traceback.format_exc())

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
            if data["on_concluido"] and hasattr(instancia, "concluido"):
                instancia.concluido.connect(data["on_concluido"])

            self._build_module_layout(data["container"], instancia)
            data["carregado"] = True
        except Exception:
            logger.error(traceback.format_exc())

    def _build_module_layout(self, container: QtWidgets.QWidget, modulo: Any):
        data = self._lazy_registry.get(container)
        container.setProperty("modulo_instancia", modulo)

        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        center = QtWidgets.QWidget()
        data["layout_central"] = QtWidgets.QVBoxLayout(center)
        data["layout_central"].setContentsMargins(0, 0, 0, 0)

        if hasattr(modulo, "get_workspace_toolbar") and (tb := modulo.get_workspace_toolbar()):
            data["layout_central"].addWidget(tb)

        if hasattr(modulo, "get_workspace") and (vw := modulo.get_workspace()):
            data["layout_central"].addWidget(vw, 1)

        data["sidebar"] = ToolboxesManager()
        if hasattr(modulo, 'get_toolboxes'):
            for label, widget in modulo.get_toolboxes().items():
                data["sidebar"].adicionar_widget(label, widget)

        splitter.addWidget(center)
        splitter.addWidget(data["sidebar"])
        splitter.setStretchFactor(0, 1)
        layout.addWidget(splitter)

    def get_modulo_ativo(self) -> Optional[Any]:
        current = self.container_paginas.currentWidget()
        return current.property("modulo_instancia") if current else None

    def _sync_active_view(self):
        if modulo := self.get_modulo_ativo():
            QtCore.QTimer.singleShot(10, lambda: self._refresh_viewer(modulo))

    def _refresh_viewer(self, modulo: Any):
        viewer = getattr(modulo, 'viewer', None)
        if hasattr(viewer, 'refresh_display'):
            viewer.refresh_display()

    def _on_componente_configurado(self, categoria, caminho, ativo):
        modulo = self.get_modulo_ativo()
        container = self.container_paginas.currentWidget()
        data = self._lazy_registry.get(container)

        if not modulo or not data: return

        if ativo:
            comp = ComponentLoader.carregar(caminho, modulo)
            if not comp: return
            if categoria == "toolbars":
                data["layout_central"].insertWidget(0, comp)
            elif categoria == "toolboxes":
                idx = data["sidebar"].adicionar_widget(caminho.stem.title(), comp)
                data["sidebar"].stack.setCurrentIndex(idx)
        else:
            self._remover_componente(categoria, caminho, data)

    def _remover_componente(self, categoria, caminho, data):
        if categoria == "toolbars":
            layout = data["layout_central"]
            for i in range(layout.count()):
                w = layout.itemAt(i).widget()
                if w and getattr(w, '__module_path__', None) == caminho:
                    w.setParent(None)
                    w.deleteLater()

    def count(self):
        return self.container_paginas.count()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    workspace = WorkspaceManager()
    workspace.resize(1200, 800)
    workspace.show()

    sys.exit(app.exec())