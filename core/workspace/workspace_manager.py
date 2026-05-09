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

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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
        self.current_patient_path = ""  # Atributo para armazenar o caminho do paciente
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
        self.btn_config.clicked.connect(self._abrir_seletor_componentes)

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

    def _abrir_seletor_componentes(self):
        if not self._config_window:
            self._config_window = Components_List(self)
            self._config_window.componente_alterado.connect(self._on_componente_configurado)
        self._config_window.show()

    def clear(self):
        logger.debug("Iniciando limpeza completa do WorkspaceManager")

        for container, data in list(self._lazy_registry.items()):
            if instancia := data.get("instancia"):
                self._cleanup_module_instance(instancia)

        while self.tab_bar.count():
            self.tab_bar.removeTab(0)

        while self.container_paginas.count():
            w = self.container_paginas.widget(0)
            self.container_paginas.removeWidget(w)
            w.setProperty("modulo_instancia", None)
            w.deleteLater()

        self._lazy_registry.clear()
        gc.collect()
        logger.debug("Limpeza completa do WorkspaceManager finalizada")

    def _cleanup_module_instance(self, instancia: Any):
        try:
            if hasattr(instancia, "concluido"):
                instancia.concluido.disconnect()
            if hasattr(instancia, "_cleanup"):
                instancia._cleanup()
        except Exception as e:
            logger.warning(f"Erro durante cleanup da instância do módulo: {e}")

    def adicionar_modulo(self, id_modulo: str, modulo_ref: Any, on_concluido=None):
        try:
            is_class = isinstance(modulo_ref, type)

            if is_class:
                instancia_temp = modulo_ref()
                title = getattr(instancia_temp, 'nome', id_modulo.replace("_", " ").capitalize())
                logger.debug(f"Módulo lazy-loading '{id_modulo}' registrado com título: '{title}'")
                del instancia_temp
            else:
                title = getattr(modulo_ref, 'nome', id_modulo.replace("_", " ").capitalize())
                logger.debug(f"Módulo '{id_modulo}' carregado com título: '{title}'")

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

            # Inicializar módulo se necessário
            if instancia := data.get("instancia"):
                if self.current_patient_path and hasattr(instancia, 'inicializar'):
                    if not hasattr(instancia, 'pasta_paciente') or not instancia.pasta_paciente:
                        instancia.inicializar(self.current_patient_path)

            self._sync_active_view()

    def _load_lazy_module(self, data: Dict):
        try:
            instancia = data["classe"]()
            data["instancia"] = instancia
            if data["on_concluido"] and hasattr(instancia, "concluido"):
                instancia.concluido.connect(data["on_concluido"])

            titulo_tab = getattr(instancia, 'nome', data["id"])
            tab_index = self.container_paginas.indexOf(data["container"])
            if tab_index >= 0:
                self.tab_bar.setTabText(tab_index, titulo_tab)

            self._build_module_layout(data["container"], instancia)
            data["carregado"] = True
            logger.debug(f"Módulo lazy '{data['id']}' foi carregado e inicializado")
        except Exception:
            logger.error(traceback.format_exc())

    def _build_module_layout(self, container: QtWidgets.QWidget, modulo: Any):
        data = self._lazy_registry.get(container)
        if not data:
            return

        container.setProperty("modulo_instancia", weakref.ref(modulo))

        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        center_widget = QtWidgets.QWidget()
        data["layout_central"] = QtWidgets.QVBoxLayout(center_widget)
        data["layout_central"].setContentsMargins(0, 0, 0, 0)

        if hasattr(modulo, "get_workspace_toolbar") and (tb := modulo.get_workspace_toolbar()):
            data["layout_central"].addWidget(tb)
        if hasattr(modulo, "get_workspace") and (vw := modulo.get_workspace()):
            data["layout_central"].addWidget(vw, 1)

        data["sidebar"] = ToolboxesManager()
        if hasattr(data["sidebar"], "layout") and data["sidebar"].layout():
            data["sidebar"].layout().setAlignment(QtCore.Qt.AlignTop)

        if hasattr(modulo, 'get_toolboxes'):
            for label, widget in modulo.get_toolboxes().items():
                data["sidebar"].adicionar_widget(label, widget)

        splitter.addWidget(center_widget)
        splitter.addWidget(data["sidebar"])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        layout.addWidget(splitter)

    def get_modulo_ativo(self) -> Optional[Any]:
        current = self.container_paginas.currentWidget()
        if current:
            ref = current.property("modulo_instancia")
            return ref() if isinstance(ref, weakref.ReferenceType) else ref
        return None

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
                nome_toolbox = getattr(comp, 'toolbox_name', caminho.stem.title())
                idx = data["sidebar"].adicionar_widget(nome_toolbox, comp)
                data["sidebar"].stack.setCurrentIndex(idx)
        else:
            self._remover_componente(categoria, caminho, data)

    def _remover_componente(self, categoria, caminho, data):
        if categoria == "toolbars":
            layout = data["layout_central"]
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if not item: continue
                w = item.widget()
                if w and getattr(w, '__module_path__', None) == caminho:
                    self._desconectar_sinais_componente(w)
                    layout.removeWidget(w)
                    w.setParent(None)
                    w.deleteLater()
                    logger.debug(f"Componente toolbar removido: {caminho}")
                    break
        elif categoria == "toolboxes":
            sidebar = data.get("sidebar")
            if sidebar and hasattr(sidebar, 'remover_widget_por_caminho'):
                sidebar.remover_widget_por_caminho(caminho)

    def _desconectar_sinais_componente(self, componente: QtWidgets.QWidget):
        try:
            if hasattr(componente, 'destroyed'):
                componente.destroyed.disconnect()
        except Exception as e:
            logger.warning(f"Erro ao desconectar sinais do componente: {e}")

    def verificar_limpeza_memoria(self) -> Dict[str, int]:
        stats = {
            "containers_ativos": self.container_paginas.count(),
            "tabs_ativas": self.tab_bar.count(),
            "registros_lazy": len(self._lazy_registry),
            "widgets_nao_deletados": 0
        }

        for container in self._lazy_registry.keys():
            if not container.parent():
                stats["widgets_nao_deletados"] += 1

        return stats

    def count(self):
        return self.container_paginas.count()

    def set_patient_path(self, path: str):
        """Define o caminho do paciente no workspace."""
        self.current_patient_path = path


if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets

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
                    "Configurações": QtWidgets.QLabel("Configurações rápidas")
                }

        workspace.adicionar_modulo("test_module", TestModule())

        class AnotherTest:
            nome = "Visualizador"

            def get_workspace(self):
                from PySide6.QtWidgets import QTextEdit
                text = QTextEdit()
                text.setPlainText(
                    "Área de trabalho principal do Visualizador.\n\nAqui viria o conteúdo principal do módulo.")
                return text

        workspace.adicionar_modulo("viewer", AnotherTest())

    except Exception as e:
        logger.error(f"Erro ao adicionar módulos de teste: {e}")

    workspace.show()

    logger.info("WorkspaceManager iniciado com sucesso.")
    sys.exit(app.exec())