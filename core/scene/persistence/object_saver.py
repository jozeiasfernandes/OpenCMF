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
        """
        Serializa objetos para string JSON.

        Se ``objects`` for omitido, usa ``registry.all()`` (ordem do dict interno).
        """
        objs = list(objects) if objects is not None else self._registry.all()
        return self._serializer.save(objs)

    def save_to_file(
        self,
        path: Union[str, Path],
        *,
        objects: Optional[Iterable[SceneObject]] = None,
        encoding: str = "utf-8",
    ) -> None:
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(self.to_json(objects), encoding=encoding)
