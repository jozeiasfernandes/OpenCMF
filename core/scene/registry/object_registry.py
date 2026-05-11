'''

id -> SceneObject

SceneManager
   ↓
ObjectRegistry  ← PRÓXIMO PASSO
   ↓
SceneObject
   ↓
ActorFactory
   ↓
ActorRegistry
   ↓
Renderer

'''

from typing import Dict, Optional
from ..scene_object import SceneObject


class ObjectRegistry:
    def __init__(self):
        self._objects: Dict[str, SceneObject] = {}

    def register(self, obj: SceneObject):
        self._objects[obj.id] = obj

    def unregister(self, obj_id: str):
        self._objects.pop(obj_id, None)

    def get(self, obj_id: str) -> Optional[SceneObject]:
        return self._objects.get(obj_id)

    def has(self, obj_id: str) -> bool:
        return obj_id in self._objects

    def all(self):
        return list(self._objects.values())

    def clear(self):
        self._objects.clear()

    def count(self) -> int:
        return len(self._objects)
