import json
import dataclasses
from typing import Dict, Any, List
from ..scene_object import SceneObject


class Serializer:
    def save(self, objects: List[SceneObject]) -> str:
        data = [self._serialize(obj) for obj in objects]
        return json.dumps(data, indent=2, ensure_ascii=False)

    def load(self, raw: str) -> List[SceneObject]:
        try:
            data = json.loads(raw)
            return [self._deserialize(item) for item in data]
        except (json.JSONDecodeError, TypeError, KeyError):
            return []

    def _serialize(self, obj: SceneObject) -> Dict[str, Any]:
        data = dataclasses.asdict(obj)
        data.pop("vtk_actor_ref", None)
        data.pop("mesh_data", None)
        return data

    def _deserialize(self, data: Dict[str, Any]) -> SceneObject:
        fields = {f.name for f in dataclasses.fields(SceneObject)}
        clean_data = {
            key: value
            for key, value in data.items()
            if key in fields
        }

        if "color" in clean_data and isinstance(clean_data["color"], list):
            clean_data["color"] = tuple(clean_data["color"])

        return SceneObject(**clean_data)