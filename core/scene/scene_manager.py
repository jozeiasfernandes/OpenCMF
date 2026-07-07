from typing import Optional, List, Any, Dict
from .scene_object import SceneObject
from .scene_state import SceneState
from .events.event_bus import EventBus
from .events.scene_events import (
    OBJECT_ADDED,
    OBJECT_REMOVED,
    OBJECT_UPDATED,
    VISIBILITY_CHANGED,
    SELECTION_CHANGED,
)
from .registry.object_registry import ObjectRegistry
from .registry.actor_registry import ActorRegistry
from .selection.selection_manager import SelectionManager


class SceneManager:
    def __init__(
            self,
            state: SceneState,
            event_bus: EventBus,
            object_registry: ObjectRegistry,
            selection_manager: SelectionManager,
            transform_manager: Any = None
    ):
        self.state = state
        self.events = event_bus
        self.objects = object_registry
        self.selection = selection_manager
        self.transform_manager = transform_manager

    def add_object(self, obj: SceneObject):
        self.objects.register(obj)
        self.events.emit(OBJECT_ADDED, object_id=obj.id, obj=obj)

    def remove_object(self, obj_id: str):
        if not self.objects.has(obj_id):
            return
        self.objects.unregister(obj_id)
        self.selection.deselect(obj_id)

        # O Bridge escutará este evento e lidará com o ActorRegistry e Renderer
        self.events.emit(OBJECT_REMOVED, object_id=obj_id)

        self.objects.unregister(obj_id)
        # O ActorRegistry agora é o único responsável pela gestão visual,
        # e o SceneManager orquestra a limpeza.
        self.actors.unregister(obj_id)
        self.selection.deselect(obj_id)

        self.events.emit(OBJECT_REMOVED, object_id=obj_id)

    def select_object(self, obj_id: Optional[str], multi: bool = False):
        """Delega a lógica de seleção ao SelectionManager."""
        if obj_id:
            self.selection.select(obj_id, exclusive=not multi)
        else:
            self.selection.clear()