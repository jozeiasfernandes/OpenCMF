from typing import Optional, Any
from .scene_object import SceneObject
from .scene_state import SceneState
from .events.event_bus import EventBus
from .events.scene_events import SceneEvents
from .registry.object_registry import ObjectRegistry
from .registry.actor_registry import ActorRegistry
from .selection.selection_manager import SelectionManager
from .io.importer import ObjectImporter


class SceneManager:
    def __init__(
            self,
            state: SceneState,
            event_bus: EventBus,
            object_registry: ObjectRegistry,
            actor_registry: ActorRegistry,
            selection_manager: SelectionManager,
            importer: ObjectImporter,
            transform_manager: Any = None
    ):
        self.state = state
        self.events = event_bus
        self.objects = object_registry
        self.actors = actor_registry
        self.selection = selection_manager
        self.importer = importer
        self.transform_manager = transform_manager

    def import_and_add(self, file_path: str, category: str):
        obj = self.importer.import_external_file(file_path, category)
        if obj:
            self.add_object(obj)
            return obj
        return None

    def add_object(self, obj: SceneObject):
        self.objects.register(obj)
        self.events.emit(SceneEvents.OBJECT_ADDED, object_id=obj.id, obj=obj)

    def remove_object(self, obj_id: str):
        obj = self.objects.get(obj_id)
        if not obj:
            return

        self.objects.unregister(obj_id)
        self.actors.unregister(obj_id)
        self.selection.deselect(obj_id)

        if hasattr(obj, 'file_path') and obj.file_path:
            self.importer.delete_physical_file(obj.file_path)

        self.events.emit(SceneEvents.OBJECT_REMOVED, object_id=obj_id)

    def select_object(self, obj_id: Optional[str], multi: bool = False):
        if obj_id:
            self.selection.select(obj_id, exclusive=not multi)
        else:
            self.selection.clear()