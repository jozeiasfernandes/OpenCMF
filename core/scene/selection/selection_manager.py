from typing import List, Optional
from core.scene.events.scene_events import SELECTION_CHANGED
# Importe o seu SceneState aqui
from core.scene.scene_state import SceneState


class SelectionManager:
    """
    Gerencia a seleção de objetos manipulando diretamente o SceneState.
    Atua como um serviço (controller) e não como um repositório de dados.
    """

    def __init__(self, state: SceneState, event_bus=None):
        self.state = state
        self._bus = event_bus

    @property
    def selected_ids(self) -> List[str]:
        """Retorna uma lista da seleção atual baseada no SceneState."""
        return list(self.state.selected_object_ids)

    def _emit(self):
        """Notifica o sistema de que a seleção mudou."""
        if self._bus:
            self._bus.emit(SELECTION_CHANGED, selected_ids=self.selected_ids)

    def select(self, obj_id: str, exclusive: bool = True):
        """Adiciona um objeto à seleção no SceneState."""
        if not obj_id:
            return

        if exclusive:
            # Substitui o conjunto atual pelo novo
            self.state.selected_object_ids = {obj_id}
        else:
            # Adiciona ao conjunto existente
            self.state.selected_object_ids.add(obj_id)

        self._emit()

    def deselect(self, obj_id: str):
        """Remove um objeto da seleção no SceneState."""
        if obj_id in self.state.selected_object_ids:
            self.state.selected_object_ids.discard(obj_id)
            self._emit()

    def toggle(self, obj_id: str):
        """Alterna o estado de seleção de um objeto."""
        if obj_id in self.state.selected_object_ids:
            self.deselect(obj_id)
        else:
            self.select(obj_id, exclusive=False)

    def clear(self):
        """Limpa toda a seleção do SceneState."""
        if self.state.selected_object_ids:
            self.state.selected_object_ids.clear()
            self._emit()

    def set_selection(self, ids: List[str]):
        """Define a seleção completa a partir de uma lista."""
        self.state.selected_object_ids = set(ids)
        self._emit()

    def get_first_selected(self) -> Optional[str]:
        """Retorna o primeiro ID selecionado, se existir."""
        return next(iter(self.state.selected_object_ids)) if self.state.selected_object_ids else None

    def is_selected(self, obj_id: str) -> bool:
        """Verifica se um objeto está selecionado no SceneState."""
        return obj_id in self.state.selected_object_ids