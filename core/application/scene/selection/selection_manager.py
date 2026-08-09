from typing import List, Optional
from application.scene.events.scene_events import SceneEvents
from application.scene.scene_state import SceneState


class SelectionManager:
    def __init__(self, state: SceneState, event_bus=None):
        self.state = state
        self._bus = event_bus

    @property
    def selected_ids(self) -> List[str]:
        # Retorna uma cópia para evitar mutação externa não controlada
        return list(self.state.selected_object_ids)

    def _emit(self):
        if self._bus:
            # Emitindo os dados esperados pelo seu EventBus
            self._bus.emit(SceneEvents.SELECTION_CHANGED, {"selected_ids": self.selected_ids})

    def select(self, obj_id: str, exclusive: bool = True):
        if not obj_id:
            return

        current = self.state.selected_object_ids
        if exclusive:
            if current == {obj_id}:
                return
            self.state.selected_object_ids = {obj_id}
        else:
            if obj_id in current:
                return
            # Cria uma cópia para garantir a atualização do estado
            new_selection = current.copy()
            new_selection.add(obj_id)
            self.state.selected_object_ids = new_selection

        self._emit()

    def deselect(self, obj_id: str):
        if obj_id in self.state.selected_object_ids:
            # Garante a atualização via atribuição
            new_selection = self.state.selected_object_ids.copy()
            new_selection.discard(obj_id)
            self.state.selected_object_ids = new_selection
            self._emit()

    def toggle(self, obj_id: str):
        if self.is_selected(obj_id):
            self.deselect(obj_id)
        else:
            self.select(obj_id, exclusive=False)

    def clear(self):
        if self.state.selected_object_ids:
            # Atribui um novo conjunto vazio para garantir que o estado seja notificado
            self.state.selected_object_ids = set()
            self._emit()

    def set_selection(self, ids: List[str]):
        new_ids = set(ids)
        if self.state.selected_object_ids != new_ids:
            self.state.selected_object_ids = new_ids
            self._emit()

    def get_first_selected(self) -> Optional[str]:
        try:
            return next(iter(self.state.selected_object_ids))
        except StopIteration:
            return None

    def is_selected(self, obj_id: str) -> bool:
        return obj_id in self.state.selected_object_ids