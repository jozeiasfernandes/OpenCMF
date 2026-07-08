from typing import Optional, Any
from .scene_object import SceneObject
from .scene_state import SceneState
from .events.event_bus import EventBus
from .events.scene_events import SceneEvents  # Importação corrigida
from .registry.object_registry import ObjectRegistry
from .registry.actor_registry import ActorRegistry
from .selection.selection_manager import SelectionManager


class SceneManager:
    def __init__(
            self,
            state: SceneState,
            event_bus: EventBus,
            object_registry: ObjectRegistry,
            actor_registry: ActorRegistry,  # Adicionado
            selection_manager: SelectionManager,
            transform_manager: Any = None
    ):
        self.state = state
        self.events = event_bus
        self.objects = object_registry
        self.actors = actor_registry  # Agora existe!
        self.selection = selection_manager
        self.transform_manager = transform_manager

    def add_object(self, obj: SceneObject):
        self.objects.register(obj)
        # Uso correto da classe de eventos
        self.events.emit(SceneEvents.OBJECT_ADDED, object_id=obj.id, obj=obj)

    def remove_object(self, obj_id: str):
        if not self.objects.has(obj_id):
            return

        # 1. Limpeza de registros
        self.objects.unregister(obj_id)
        self.actors.unregister(obj_id)  # Agora funciona porque definimos no __init__
        self.selection.deselect(obj_id)

        # 2. Notificação única
        self.events.emit(SceneEvents.OBJECT_REMOVED, object_id=obj_id)

    def select_object(self, obj_id: Optional[str], multi: bool = False):
        if obj_id:
            self.selection.select(obj_id, exclusive=not multi)
        else:
            self.selection.clear()