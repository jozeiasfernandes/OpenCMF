import sys
import logging
from typing import TYPE_CHECKING, Optional, Any
from PySide6 import QtWidgets, QtCore, QtGui
import vtk

from core.shortcut.shortcuts import get_shortcuts_by_scope, match_shortcut
from core.components.bases.base_central_area import CentralAreaBase
from core.components.central_area.viewer_3d_central_area import Viewer3D_Widget_CentralArea

from core.scene.scene_manager import SceneManager
from core.scene.selection.selection_manager import SelectionManager
from core.scene.events.scene_events import SceneEvents, RegistrationEvents
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.events.event_bus import EventBus
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.scene_state import SceneState


logger = logging.getLogger("OpenCMF.ViewerRegistration_Widget_CentralArea")


class ViewerRegistration_Widget_CentralArea(CentralAreaBase):
    """
    Widget central para registro de objetos.
    Herda de CentralAreaBase para integração com a arquitetura.
    """
    pontoAdicionado = QtCore.Signal(str, list)
    requisitarCarregamentoObjeto = QtCore.Signal(str, str)

    def __init__(self, context: Any, title: str = "Registro", parent: Optional[QtWidgets.QWidget] = None):
        self.context = context

        # 2. Inicializar CentralAreaBase
        super().__init__(context=context, title=title, cor_identificacao="#202020", usar_vtk=False, parent=parent)

        self.shortcuts = get_shortcuts_by_scope("view3d")
        self.current_mode = "select"
        self.properties_panel = None
        self._views = {}
        self._combos = {}

        # Configurar UI imediatamente
        self.setup_component()

    def setup_ui(self) -> None:
        """Configura a interface do usuário."""
        if self.layout_principal is None:
            self._setup_base_ui()

        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.top_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        for side in ["A", "B"]:
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(2)

            # CORREÇÃO: Passar self.context (que contém o scene_manager)
            # em vez de passar self.scene_manager diretamente.
            # Certifique-se de que Viewer3D_Widget_CentralArea também aceite 'context'
            view = Viewer3D_Widget_CentralArea(
                nome=f"Vista {side}",
                cor_borda="#202020",
                parent=self,
                context=self.context
            )

            combo = QtWidgets.QComboBox()
            combo.setMaximumHeight(25)
            # ... (seu estilo permanece igual)

            layout.addWidget(view, stretch=1)
            layout.addWidget(combo)

            setattr(self, f"view_{side.lower()}", view)
            setattr(self, f"combo_{side.lower()}", combo)

            self._views[side] = view
            self._combos[side] = combo

            self.top_splitter.addWidget(container)

            combo.currentTextChanged.connect(
                lambda t, s=side: self._on_combo_changed(s, t)
            )

        # Vista C (visão geral)
        self.view_c = Viewer3D_Widget_CentralArea(
            nome="Visor Geral",
            cor_borda="#202020",
            parent=self,
            context=self.context  # CORREÇÃO AQUI TAMBÉM
        )
        self._views["C"] = self.view_c

        # Configurar proporções
        self.top_splitter.setSizes([400, 400])
        self.main_splitter.addWidget(self.top_splitter)
        self.main_splitter.addWidget(self.view_c)
        self.main_splitter.setSizes([500, 300])

        self.layout_principal.addWidget(self.main_splitter)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._bind_scene_listeners()

    @property
    def scene_manager(self):
        if hasattr(self, '_context') and self._context:
            return self._context.scene_manager
        return None

    @property
    def view_registration(self):
        """Retorna a referência para si mesmo (compatibilidade)."""
        return self

    def _bind_scene_listeners(self) -> None:
        """Conecta os listeners da cena."""
        if not self.scene_manager:
            return

        bus = self.scene_manager.events
        bus.subscribe(SceneEvents.VISIBILITY_CHANGED, self._on_scene_bus_visibility)
        bus.subscribe(SceneEvents.OBJECT_UPDATED, self._on_scene_bus_object_updated)
        bus.subscribe(SceneEvents.OBJECT_REMOVED, self._on_scene_bus_object_removed)
        bus.subscribe(SceneEvents.INTERACTION_MODE_CHANGED, self.set_interaction_mode)

    def _on_combo_changed(self, vista_id: str, nome_objeto: str):
        """Callback quando um combo é alterado."""
        if nome_objeto and self.scene_manager:
            event_key = RegistrationEvents.TARGET_CHANGED if vista_id == "A" else RegistrationEvents.SOURCE_CHANGED

            self.scene_manager.events.emit(
                event_key,
                object_id=nome_objeto
            )

            self.requisitarCarregamentoObjeto.emit(vista_id, nome_objeto)

    def set_interaction_mode(self, mode: str, **kwargs):
        """Define o modo de interação."""
        self.current_mode = mode
        cursor = QtCore.Qt.ArrowCursor if mode == "select" else QtCore.Qt.CrossCursor

        if hasattr(self, 'view_a'):
            self.view_a.setCursor(cursor)
            if hasattr(self.view_a, 'set_interactor_style'):
                self.view_a.set_interactor_style(mode)

        if hasattr(self, 'view_b'):
            self.view_b.setCursor(cursor)
            if hasattr(self.view_b, 'set_interactor_style'):
                self.view_b.set_interactor_style(mode)

    def _on_scene_bus_visibility(self, object_id: str, visible: bool, **_kwargs):
        """Callback para mudança de visibilidade."""
        for view in self._views.values():
            if hasattr(view, 'vtk_scene_renderer'):
                view.vtk_scene_renderer.set_visibility(object_id, visible)
                view.render()

    def _on_scene_bus_object_updated(self, object_id: str, **kwargs):
        """Callback para atualização de objeto."""
        prop = kwargs.get("property")
        val = kwargs.get("value")
        for view in self._views.values():
            if hasattr(view, 'vtk_scene_renderer'):
                view.vtk_scene_renderer.update_property(object_id, prop, val)
                view.render()

    def _on_scene_bus_object_removed(self, object_id: str, **_kwargs):
        """Callback para remoção de objeto."""
        for view in self._views.values():
            if hasattr(view, 'vtk_scene_renderer'):
                view.vtk_scene_renderer.remove_actor(object_id)
                view.render()

    def _get_active_view(self):
        """Retorna a view ativa."""
        for view in self._views.values():
            if view.hasFocus():
                return view
        return self.view_c

    # ==================== Métodos para compatibilidade com o módulo principal ====================

    def atualizar_combos(self, lista_objetos: list):
        """
        Atualiza os combos com a lista de objetos.
        Compatível com o método esperado pelo módulo principal.
        """
        # Se lista_objetos for uma lista de dicionários com 'id' e 'name'
        if lista_objetos and isinstance(lista_objetos[0], dict):
            nomes = [obj['name'] for obj in lista_objetos]
        else:
            nomes = lista_objetos

        for combo in self._combos.values():
            current_text = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("")
            combo.addItems(nomes)
            if current_text in nomes:
                combo.setCurrentText(current_text)
            combo.blockSignals(False)

    def adicionar_malha_vista_a(self, nome: str, poly_data, obj_id: str):
        """Adiciona uma malha à vista A."""
        if hasattr(self, 'view_a') and hasattr(self.view_a, 'vtk_scene_renderer'):
            self.view_a.vtk_scene_renderer.add_actor(obj_id, poly_data, nome)
            self.view_a.render()

    def adicionar_malha_vista_b(self, nome: str, poly_data, obj_id: str):
        """Adiciona uma malha à vista B."""
        if hasattr(self, 'view_b') and hasattr(self.view_b, 'vtk_scene_renderer'):
            self.view_b.vtk_scene_renderer.add_actor(obj_id, poly_data, nome)
            self.view_b.render()

    def limpar_marcadores(self):
        """Limpa os marcadores das vistas."""
        for view in [self.view_a, self.view_b]:
            if hasattr(view, 'vtk_scene_renderer') and hasattr(view.vtk_scene_renderer, 'clear_markers'):
                view.vtk_scene_renderer.clear_markers()
                view.render()

    def limpar_tabela(self):
        """Limpa a tabela de pontos."""
        # Implementar conforme necessário
        pass

    def connect_properties_panel(self, properties_panel):
        """Conecta o painel de propriedades."""
        self.properties_panel = properties_panel
        logger.debug("Painel de propriedades conectado")

    def limpar_objeto(self, object_id: str):
        """Remove um objeto das vistas."""
        for view in self._views.values():
            if hasattr(view, 'vtk_scene_renderer'):
                view.vtk_scene_renderer.remove_actor(object_id)
                view.render()

    def keyPressEvent(self, event):
        """Processa eventos de teclado."""
        action = match_shortcut(event, self.shortcuts)
        if action:
            self.execute_action(action, self._get_active_view())
            event.accept()
        else:
            super().keyPressEvent(event)

    def execute_action(self, action, view):
        """Executa uma ação de atalho."""
        logger.debug(f"Executando ação: {action}")
        # Implementar ações específicas aqui

    def dispose(self):
        """Limpeza de recursos."""
        # Desconectar listeners
        if self.scene_manager and self.scene_manager.events:
            bus = self.scene_manager.events
            bus.unsubscribe(SceneEvents.VISIBILITY_CHANGED, self._on_scene_bus_visibility)
            bus.unsubscribe(SceneEvents.OBJECT_UPDATED, self._on_scene_bus_object_updated)
            bus.unsubscribe(SceneEvents.OBJECT_REMOVED, self._on_scene_bus_object_removed)
            bus.unsubscribe(SceneEvents.INTERACTION_MODE_CHANGED, self.set_interaction_mode)

        super().dispose()

    @property
    def scene_manager(self):
        # Você está checando '_context', mas definiu 'self.context'
        if hasattr(self, 'context') and self.context:
            return self.context.scene_manager
        return None


if __name__ == "__main__":
    # Garante que o QApplication exista antes de criar qualquer Widget
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)


    class FakeContext:
        """Simula o contexto necessário para a injeção de dependência."""

        def __init__(self):
            self.event_bus = EventBus()
            self.scene_state = SceneState()
            self.object_registry = ObjectRegistry()
            self.actor_registry = ActorRegistry()

            # O atributo .scene_manager é obrigatório para o BaseComponent
            self.scene_manager = SceneManager(
                state=self.scene_state,
                event_bus=self.event_bus,
                object_registry=self.object_registry,
                actor_registry=self.actor_registry,
                selection_manager=SelectionManager(self.event_bus, self.scene_state),
                importer=None,
                transform_manager=None
            )
            self.project_service = None


    # Instanciação do contexto mock
    context = FakeContext()

    # Configuração da janela principal
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Teste de Registro")
    window.resize(1024, 768)

    try:
        # Instanciação do Widget
        registration_widget = ViewerRegistration_Widget_CentralArea(context=context, title="Registro")
        window.setCentralWidget(registration_widget)

        window.show()
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Erro ao inicializar widget de teste: {e}", exc_info=True)
        sys.exit(1)