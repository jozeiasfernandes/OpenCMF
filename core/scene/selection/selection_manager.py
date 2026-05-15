from typing import List, Set, Optional
from core.scene.events.scene_events import SELECTION_CHANGED


class SelectionManager:
    def __init__(self, event_bus=None):
        self._selected_ids: Set[str] = set()
        self._bus = event_bus

    @property
    def selected_ids(self) -> List[str]:
        return list(self._selected_ids)

    def _emit(self):
        if self._bus:
            self._bus.emit(SELECTION_CHANGED, selected_ids=self.selected_ids)

    def select(self, obj_id: str, exclusive: bool = True):
        if not obj_id:
            return

        if exclusive:
            if len(self._selected_ids) == 1 and obj_id in self._selected_ids:
                return
            self._selected_ids.clear()

        self._selected_ids.add(obj_id)
        self._emit()

    def deselect(self, obj_id: str):
        if obj_id in self._selected_ids:
            self._selected_ids.discard(obj_id)
            self._emit()

    def toggle(self, obj_id: str):
        if obj_id in self._selected_ids:
            self._selected_ids.remove(obj_id)
        else:
            self._selected_ids.add(obj_id)
        self._emit()

    def clear(self):
        if self._selected_ids:
            self._selected_ids.clear()
            self._emit()

    def set_selection(self, ids: List[str]):
        self._selected_ids = set(ids)
        self._emit()

    def get_first_selected(self) -> Optional[str]:
        return next(iter(self._selected_ids)) if self._selected_ids else None

    def is_selected(self, obj_id: str) -> bool:
        return obj_id in self._selected_ids