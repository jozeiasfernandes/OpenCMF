'''

Persiste objetos da cena (JSON).

Simétrico a ObjectLoader: usa Serializer + ObjectRegistry.

'''

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Union

from .serializer import Serializer
from ..registry.object_registry import ObjectRegistry
from ..scene_object import SceneObject


class ObjectSaver:
    def __init__(self, serializer: Serializer, registry: ObjectRegistry):
        self._serializer = serializer
        self._registry = registry

    def to_json(self, objects: Optional[Iterable[SceneObject]] = None) -> str:
        target_objects = list(objects) if objects is not None else self._registry.all()
        return self._serializer.save(target_objects)

    def save_to_file(
        self,
        path: Union[str, Path],
        *,
        objects: Optional[Iterable[SceneObject]] = None,
        encoding: str = "utf-8",
    ) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        json_content = self.to_json(objects)
        file_path.write_text(json_content, encoding=encoding)
