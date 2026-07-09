from typing import List, Optional
from core.scene.events.scene_events import SceneEvents
from core.scene.scene_state import SceneState


class SelectionManager:
    def __init__(self, state: SceneState, event_bus=None):
        self.state = state
        self._bus = event_bus

    @property
    def selected_ids(self) -> List[str]:
        return list(self.state.selected_object_ids)

    def _emit(self):
        if self._bus:
            self._bus.emit(SceneEvents.SELECTION_CHANGED, selected_ids=self.selected_ids)

    def select(self, obj_id: str, exclusive: bool = True):
        if not obj_id:
            return
        if exclusive:
            if self.state.selected_object_ids == {obj_id}:
                return
            self.state.selected_object_ids = {obj_id}
        else:
            if obj_id in self.state.selected_object_ids:
                return
            self.state.selected_object_ids.add(obj_id)

        self._emit()

    def deselect(self, obj_id: str):
        if obj_id in self.state.selected_object_ids:
            self.state.selected_object_ids.discard(obj_id)
            self._emit()

    def toggle(self, obj_id: str):
        if obj_id in self.state.selected_object_ids:
            self.deselect(obj_id)
        else:
            self.select(obj_id, exclusive=False)

    def clear(self):
        if self.state.selected_object_ids:
            self.state.selected_object_ids.clear()
            self._emit()

    def set_selection(self, ids: List[str]):
        new_ids = set(ids)
        if self.state.selected_object_ids != new_ids:
            self.state.selected_object_ids = new_ids
            self._emit()

    def get_first_selected(self) -> Optional[str]:
        return next(iter(self.state.selected_object_ids)) if self.state.selected_object_ids else None

    def is_selected(self, obj_id: str) -> bool:
        return obj_id in self.state.selected_object_ids