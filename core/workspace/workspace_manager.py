import sys
import logging
import traceback
import weakref
import gc
from pathlib import Path
from typing import Optional, Any, Dict

from PySide6 import QtWidgets, QtCore, QtGui

from core.workspace.toolboxes_manager import ToolboxesManager
from core.workspace.loader_components import ComponentLoader
from core.workspace.componentes_list import Components_List

logger = logging.getLogger("WorkspaceManager")


def get_resource_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


class WorkspaceManager(QtWidgets.QWidget):
    home_solicitada = QtCore.Signal()
    currentChanged = QtCore.Signal(int)

    def __init__(self):
        super().__init__()
        self.base_dir = get_resource_path()
        self._lazy_registry: Dict[QtWidgets.QWidget, Dict[str, Any]] = {}
        self._config_window = None
        self.current_patient_path = ""
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
        self._apply_icon(self.btn_home, "home.svg")
        self.btn_home.clicked.connect(self.home_solicitada.emit)

        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        self.btn_config = QtWidgets.QPushButton()
        self.btn_config.setFixedSize(30, 30)
        self._apply_icon(self.btn_config, "config_branco.svg")
        self.btn_config.clicked.connect(self._abrir_seletor_componentes)

        header_grid.addWidget(self.btn_home, 0, 0)
        header_grid.addWidget(self.tab_bar, 0, 1)
        header_grid.setColumnStretch(2, 1)
        header_grid.addWidget(self.btn_config, 0, 3)

        self.container_paginas = QtWidgets.QStackedWidget()
        self.layout_principal.addWidget(self.header)
        self.layout_principal.addWidget(self.container_paginas)

    def _apply_icon(self, button, name):
        path = self.base_dir / "appearance" / "icons" / name
        icon = QtGui.QIcon(str(path))
        button.setIcon(icon)
        button.setCursor(QtCore.Qt.PointingHandCursor)

    def set_patient_path(self, path: str):
        if self.current_patient_path == path:
            return
        self.current_patient_path = path
        if modulo := self.get_modulo_ativo():
            self._safe_inicializar(modulo)

    def clear(self):
        logger.debug("Iniciando limpeza do WorkspaceManager")
        for data in self._lazy_registry.values():
            if inst := data.get("instancia"):
                self._cleanup_module_instance(inst)

        while self.tab_bar.count():
            self.tab_bar.removeTab(0)
        while self.container_paginas.count():
            w = self.container_paginas.widget(0)
            self.container_paginas.removeWidget(w)
            w.deleteLater()

        self._lazy_registry.clear()
        gc.collect()

    def _cleanup_module_instance(self, instancia: Any):
        try:
            if hasattr(instancia, "concluido"):
                instancia.concluido.disconnect()
            if hasattr(instancia, "_cleanup"):
                instancia._cleanup()
        except Exception:
            pass

    def adicionar_modulo(self, id_modulo: str, modulo_ref: Any, on_concluido=None):
        is_class = isinstance(modulo_ref, type)
        title = id_modulo.replace("_", " ").capitalize()

        if is_class:
            try:
                temp = modulo_ref()
                title = getattr(temp, 'nome', title)
                del temp
            except Exception:
                pass
        else:
            title = getattr(modulo_ref, 'nome', title)

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
        }

        if not is_class:
            # FIX #3: conectar on_concluido também para instâncias diretas (não-lazy)
            if on_concluido and hasattr(modulo_ref, "concluido"):
                modulo_ref.concluido.connect(on_concluido)
            self._build_module_layout(container, modulo_ref)

        if self.tab_bar.count() == 1:
            self._on_tab_changed(0)

    def _on_tab_changed(self, index: int):
        if index < 0:
            return
        self.container_paginas.setCurrentIndex(index)
        self.currentChanged.emit(index)

        container = self.container_paginas.widget(index)
        if data := self._lazy_registry.get(container):
            if not data["carregado"]:
                self._load_lazy_module(data)
            # FIX #4: adiar inicializar para após o widget estar visível/dimensionado
            if inst := data.get("instancia"):
                QtCore.QTimer.singleShot(0, lambda i=inst: self._safe_inicializar(i))
            self._sync_active_view()

    def _safe_inicializar(self, instancia: Any):
        if not self.current_patient_path:
            return
        path_modulo = getattr(instancia, 'pasta_paciente', None)
        if str(path_modulo) != str(self.current_patient_path):
            if hasattr(instancia, 'inicializar'):
                instancia.inicializar(self.current_patient_path)

    def _load_lazy_module(self, data: Dict):
        try:
            instancia = data["classe"]()
            data["instancia"] = instancia
            if data["on_concluido"] and hasattr(instancia, "concluido"):
                instancia.concluido.connect(data["on_concluido"])

            tab_idx = self.container_paginas.indexOf(data["container"])
            self.tab_bar.setTabText(tab_idx, getattr(instancia, 'nome', data["id"]))
            self._build_module_layout(data["container"], instancia)
            data["carregado"] = True
        except Exception:
            logger.error(traceback.format_exc())

    def _build_module_layout(self, container: QtWidgets.QWidget, modulo: Any):
        # FIX #1: limpar layout existente antes de construir, evitando layouts empilhados
        existing_layout = container.layout()
        if existing_layout is not None:
            # Esvaziar e descartar o layout antigo de forma segura
            while existing_layout.count():
                item = existing_layout.takeAt(0)
                if w := item.widget():
                    w.setParent(None)
                    w.deleteLater()
            QtWidgets.QWidget().setLayout(existing_layout)

        data = self._lazy_registry.get(container)
        container.setProperty("modulo_instancia", weakref.ref(modulo))

        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        center = QtWidgets.QWidget()
        layout_central = QtWidgets.QVBoxLayout(center)
        layout_central.setContentsMargins(0, 0, 0, 0)
        layout_central.setSpacing(0)
        data["layout_central"] = layout_central

        # Toolbar estática do módulo — sempre no índice 0
        if hasattr(modulo, "get_workspace_toolbar") and (tb := modulo.get_workspace_toolbar()):
            tb.setProperty("_is_static_toolbar", True)
            layout_central.addWidget(tb)

        # Workspace view — marcado para identificação de posição em inserções dinâmicas
        if hasattr(modulo, "get_workspace") and (vw := modulo.get_workspace()):
            vw.setProperty("_is_workspace_view", True)
            layout_central.addWidget(vw, 1)

        data["sidebar"] = ToolboxesManager()
        if hasattr(modulo, 'get_toolboxes'):
            for label, widget in modulo.get_toolboxes().items():
                data["sidebar"].adicionar_widget(label, widget)

        splitter.addWidget(center)
        splitter.addWidget(data["sidebar"])
        splitter.setStretchFactor(0, 1)
        layout.addWidget(splitter)

    def get_modulo_ativo(self) -> Optional[Any]:
        if current := self.container_paginas.currentWidget():
            ref = current.property("modulo_instancia")
            return ref() if isinstance(ref, weakref.ReferenceType) else ref
        return None

    def _sync_active_view(self):
        if mod := self.get_modulo_ativo():
            QtCore.QTimer.singleShot(10, lambda: self._refresh_viewer(mod))

    def _refresh_viewer(self, modulo: Any):
        viewer = getattr(modulo, 'viewer', None)
        if hasattr(viewer, 'refresh_display'):
            viewer.refresh_display()

    def _abrir_seletor_componentes(self):
        if not self._config_window:
            self._config_window = Components_List(self)
            self._config_window.componente_alterado.connect(self._on_componente_configurado)
        self._config_window.show()

    def _on_componente_configurado(self, categoria, caminho, ativo):
        modulo = self.get_modulo_ativo()
        data = self._lazy_registry.get(self.container_paginas.currentWidget())
        if not modulo or not data:
            return

        if ativo:
            comp = ComponentLoader.carregar(caminho, modulo)
            if not comp:
                return
            if categoria == "toolbars":
                # FIX #2: inserir toolbar dinâmica ANTES do workspace view,
                # respeitando qualquer toolbar estática já presente
                layout = data["layout_central"]
                insert_pos = 0
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    w = item.widget() if item else None
                    if w and w.property("_is_workspace_view"):
                        # inserir imediatamente antes do workspace view
                        insert_pos = i
                        break
                    insert_pos = i + 1
                comp.setProperty("__module_path__", caminho)
                layout.insertWidget(insert_pos, comp)
            elif categoria == "toolboxes":
                idx = data["sidebar"].adicionar_widget(
                    getattr(comp, 'toolbox_name', caminho.stem.title()), comp
                )
                data["sidebar"].stack.setCurrentIndex(idx)
        else:
            self._remover_componente(categoria, caminho, data)

    def _remover_componente(self, categoria, caminho, data):
        if categoria == "toolbars":
            layout = data["layout_central"]
            for i in range(layout.count()):
                item = layout.itemAt(i)
                w = item.widget() if item else None
                if w and w.property("__module_path__") == caminho:
                    layout.removeWidget(w)
                    w.setParent(None)
                    w.deleteLater()
                    break
        elif categoria == "toolboxes":
            if sb := data.get("sidebar"):
                sb.remover_widget_por_caminho(caminho)

    def count(self):
        return self.container_paginas.count()


if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets

    logging.basicConfig(level=logging.DEBUG)
    logger.info("Iniciando WorkspaceManager em modo standalone...")

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    workspace = WorkspaceManager()
    workspace.setWindowTitle("OpenCMF - Workspace Manager")
    workspace.resize(1280, 720)

    try:
        class TestModule:
            nome = "Módulo de Teste"

            def get_workspace(self):
                label = QtWidgets.QLabel("Bem-vindo ao Workspace de Teste!\n\nEste é um módulo de exemplo.")
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setStyleSheet("font-size: 18px; color: #888;")
                return label

            def get_toolboxes(self):
                return {
                    "Informações": QtWidgets.QLabel("Painel de informações do módulo"),
                    "Configurações": QtWidgets.QLabel("Configurações rápidas"),
                }

        workspace.adicionar_modulo("test_module", TestModule())

        class AnotherTest:
            nome = "Visualizador"

            def get_workspace(self):
                text = QtWidgets.QTextEdit()
                text.setPlainText(
                    "Área de trabalho principal do Visualizador.\n\nAqui viria o conteúdo principal do módulo."
                )
                return text

        workspace.adicionar_modulo("viewer", AnotherTest())

    except Exception as e:
        logger.error(f"Erro ao adicionar módulos de teste: {e}")

    workspace.show()
    logger.info("WorkspaceManager iniciado com sucesso.")
    sys.exit(app.exec())