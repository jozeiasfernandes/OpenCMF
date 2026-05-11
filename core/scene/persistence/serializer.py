'''
Persistência real
'''

import json
from typing import Dict, Any
from ..scene_object import SceneObject


class Serializer:
    def serialize_object(self, obj: SceneObject) -> Dict[str, Any]:
        return {
            "id": obj.id,
            "name": obj.name,
            "type": obj.type,
            "visible": obj.visible,
            "opacity": obj.opacity,
            "color": obj.color,
            "transform": obj.transform,
            "metadata": obj.metadata,
            "file_path": obj.file_path,
        }

    def deserialize_object(self, data: Dict[str, Any]) -> SceneObject:
        return SceneObject(
            id=data["id"],
            name=data.get("name", "Object"),
            type=data.get("type", "generic"),
            visible=data.get("visible", True),
            opacity=data.get("opacity", 1.0),
            color=tuple(data.get("color", (1.0, 1.0, 1.0))),
            transform=data.get("transform", {
                "position": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0],
            }),
            metadata=data.get("metadata", {}),
            file_path=data.get("file_path"),
            vtk_actor_ref=None,
        )

    def save(self, objects: list[SceneObject]) -> str:
        data = [self.serialize_object(obj) for obj in objects]
        return json.dumps(data, indent=2)

    def load(self, raw: str) -> list[SceneObject]:
        data = json.loads(raw)
        return [self.deserialize_object(obj) for obj in data]