'''
SceneManager → Registries → EventBus → Observers


recebe comandos
conversa com registries
emite eventos
sincroniza estado

scene.add_object(...)
scene.remove_object(...)
scene.select_object(...)
scene.update_visibility(...)

Ele NÃO:

renderiza
salva JSON diretamente
manipula Qt diretamente

Separação de estados:
* SceneState (contexto)
* SelectionManager (seleção)
* ObjectRegistry (dados)
* ActorRegistry (render mapping)
'''



from typing import Optional
from .scene_object import SceneObject
from .scene_state import SceneState
from .events.event_bus import EventBus
from .registry.object_registry import ObjectRegistry
from .registry.actor_registry import ActorRegistry
from .selection.selection_manager import SelectionManager


class SceneManager:
    def __init__(
        self,
        state: SceneState,
        event_bus: EventBus,
        object_registry: ObjectRegistry,
        actor_registry: ActorRegistry,
        selection_manager: SelectionManager,
    ):
        self.state = state
        self.events = event_bus
        self.objects = object_registry
        self.actors = actor_registry
        self.selection = selection_manager

    # -------------------------
    # Object lifecycle
    # -------------------------

    def add_object(self, obj: SceneObject):
        self.objects.register(obj)

        self.events.emit(
            "OBJECT_ADDED",
            object_id=obj.id
        )

    def remove_object(self, obj_id: str):
        obj = self.objects.get(obj_id)
        if not obj:
            return

        self.objects.unregister(obj_id)
        self.actors.unregister(obj_id)
        self.selection.deselect(obj_id)

        self.events.emit(
            "OBJECT_REMOVED",
            object_id=obj_id
        )

    # -------------------------
    # Selection
    # -------------------------

    def select_object(self, obj_id: str, multi: bool = False):
        if not multi:
            self.selection.clear()

        self.selection.select(obj_id)

        self.state.selected_object_ids = self.selection.get_selected()

        self.events.emit(
            "SELECTION_CHANGED",
            selected_ids=self.state.selected_object_ids
        )

    # -------------------------
    # Property updates
    # -------------------------

    def update_visibility(self, obj_id: str, visible: bool):
        obj = self.objects.get(obj_id)
        if not obj:
            return

        obj.visible = visible

        self.events.emit(
            "VISIBILITY_CHANGED",
            object_id=obj_id,
            visible=visible
        )

    def update_opacity(self, obj_id: str, opacity: float):
        obj = self.objects.get(obj_id)
        if not obj:
            return

        obj.opacity = opacity

        self.events.emit(
            "OBJECT_UPDATED",
            object_id=obj_id,
            property="opacity",
            value=opacity
        )

    def update_color(self, obj_id: str, color):
        obj = self.objects.get(obj_id)
        if not obj:
            return

        obj.color = color

        self.events.emit(
            "OBJECT_UPDATED",
            object_id=obj_id,
            property="color",
            value=color
        )

    # -------------------------
    # Queries
    # -------------------------

    def get_object(self, obj_id: str) -> Optional[SceneObject]:
        return self.objects.get(obj_id)

    # -------------------------
    # State sync
    # -------------------------

    def sync_state(self):
        self.state.scene_metadata["object_count"] = self.objects.count()