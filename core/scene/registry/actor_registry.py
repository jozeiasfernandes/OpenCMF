'''
id -> vtkActor

Ele deve:

* mapear SceneObject.id → vtkActor
* garantir consistência com SceneObject
* permitir lifecycle control (create/update/remove)
* não conhecer SceneManager
* não conter lógica de render
* não emitir eventos

'''

from typing import Dict, Optional, Any


class ActorRegistry:
    def __init__(self):
        self._actors: Dict[str, Any] = {}

    def register(self, obj_id: str, actor: Any):
        self._actors[obj_id] = actor

    def unregister(self, obj_id: str):
        actor = self._actors.pop(obj_id, None)
        return actor

    def get(self, obj_id: str) -> Optional[Any]:
        return self._actors.get(obj_id)

    def has(self, obj_id: str) -> bool:
        return obj_id in self._actors

    def replace(self, obj_id: str, actor: Any):
        self._actors[obj_id] = actor

    def clear(self):
        self._actors.clear()