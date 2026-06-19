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
from ..tools.transforms.transform_manager import TransformManager


class SceneManager:
    def __init__(
            self,
            state: SceneState,
            event_bus: EventBus,
            object_registry: ObjectRegistry,
            actor_registry: ActorRegistry,
            selection_manager: SelectionManager,
            transform_manager: TransformManager,
    ):
        self.state = state
        self.events = event_bus
        self.objects = object_registry
        self.actors = actor_registry
        self.selection = selection_manager
        self.transform_manager = transform_manager

    def add_object(self, obj: SceneObject):
        self.objects.register(obj)
        self.events.emit(OBJECT_ADDED, object_id=obj.id, obj=obj)
        self.sync_state()

    def remove_object(self, obj_id: str):
        if not self.objects.has(obj_id):
            return
        self.objects.unregister(obj_id)
        self.actors.unregister(obj_id)
        if self.selection.is_selected(obj_id):
            self.selection.deselect(obj_id)
            self._sync_selection_to_state()
        self.events.emit(OBJECT_REMOVED, object_id=obj_id)
        self.sync_state()

    def select_object(self, obj_id: Optional[str], multi: bool = False):
        if obj_id:
            self.selection.select(obj_id, exclusive=not multi)
        else:
            self.selection.clear()
        self._sync_selection_to_state()
        self.events.emit(SELECTION_CHANGED, selected_ids=self.state.selected_object_ids)

    def update_visibility(self, obj_id: str, visible: bool):
        obj = self.objects.get(obj_id)
        if obj and obj.visible != visible:
            obj.visible = visible
            self.events.emit(VISIBILITY_CHANGED, object_id=obj_id, visible=visible)

    def update_opacity(self, obj_id: str, opacity: float):
        obj = self.objects.get(obj_id)
        if obj:
            obj.opacity = opacity
            self._emit_update(obj_id, "opacity", opacity)

    def update_color(self, obj_id: str, color: Any):
        obj = self.objects.get(obj_id)
        if obj:
            obj.color = color
            self._emit_update(obj_id, "color", color)

    def update_transform(self, obj_id: str, transform_data: Dict[str, List[float]]):
        obj = self.objects.get(obj_id)
        if obj:
            self.transform_manager.replace_transform(obj, transform_data)
            self._emit_update(obj_id, "transforms", obj.transforms)

    def _emit_update(self, obj_id: str, prop: str, value: Any):
        self.events.emit(
            OBJECT_UPDATED,
            object_id=obj_id,
            property=prop,
            value=value
        )

    def get_object(self, obj_id: str) -> Optional[SceneObject]:
        return self.objects.get(obj_id)

    def _sync_selection_to_state(self):
        self.state.selected_object_ids = list(self.selection.get_selected())

    def sync_state(self):
        self.state.scene_metadata["object_count"] = self.objects.count()
        self.state.scene_metadata["last_update"] = str(id(self))