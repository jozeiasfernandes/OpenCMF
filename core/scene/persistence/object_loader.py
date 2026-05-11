'''

Carrega objetos da pasta do paciente.

'''

from typing import List
from .serializer import Serializer
from ..registry.object_registry import ObjectRegistry
from ..scene_object import SceneObject


class ObjectLoader:
    def __init__(self, serializer: Serializer, registry: ObjectRegistry):
        self._serializer = serializer
        self._registry = registry

    def load_from_json(self, raw: str) -> List[SceneObject]:
        objects = self._serializer.load(raw)

        for obj in objects:
            self._registry.register(obj)

        return objects

    def load_into_scene(self, raw: str):
        return self.load_from_json(raw)

    def load_objects(self, objects: List[SceneObject]):
        for obj in objects:
            self._registry.register(obj)