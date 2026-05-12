from typing import Dict, Optional, List
from ..scene_object import SceneObject

class ObjectRegistry:
    def __init__(self):
        # O dicionário garante busca O(1) por ID
        self._objects: Dict[str, SceneObject] = {}

    def register(self, obj: SceneObject):
        """Adiciona ou atualiza um objeto no registro."""
        if not obj.id:
            raise ValueError("SceneObject deve possuir um ID válido para ser registrado.")
        self._objects[obj.id] = obj

    def unregister(self, obj_id: str) -> Optional[SceneObject]:
        """Remove e retorna o objeto, se existir."""
        return self._objects.pop(obj_id, None)

    def get(self, obj_id: str) -> Optional[SceneObject]:
        return self._objects.get(obj_id)

    def has(self, obj_id: str) -> bool:
        return obj_id in self._objects

    def all(self) -> List[SceneObject]:
        """Retorna todos os objetos registrados (útil para persistência)."""
        return list(self._objects.values())

    def clear(self):
        self._objects.clear()

    def count(self) -> int:
        return len(self._objects)

    def __iter__(self):
        """Permite iterar diretamente no registro: for obj in registry:"""
        return iter(self._objects.values())