'''
Centraliza seleção global.

Hoje sua seleção está espalhada:

toolbox
tabela
VTK picker

Tudo deveria convergir aqui.

'''


from typing import List, Set
from core.scene.scene_object import SceneObject


class SelectionManager:
    def __init__(self):
        self._selected_ids: Set[str] = set()

    def select(self, obj_id: str):
        self._selected_ids.add(obj_id)

    def deselect(self, obj_id: str):
        self._selected_ids.discard(obj_id)

    def toggle(self, obj_id: str):
        if obj_id in self._selected_ids:
            self._selected_ids.remove(obj_id)
        else:
            self._selected_ids.add(obj_id)

    def clear(self):
        self._selected_ids.clear()

    def set_selection(self, ids: List[str]):
        self._selected_ids = set(ids)

    def get_selected(self) -> List[str]:
        return list(self._selected_ids)

    def is_selected(self, obj_id: str) -> bool:
        return obj_id in self._selected_ids