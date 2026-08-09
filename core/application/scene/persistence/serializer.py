import json
import dataclasses
import logging
from typing import Dict, Any, List
from ..scene_object import SceneObject

logger = logging.getLogger("OpenCMF.Serializer")


class Serializer:
    def save(self, objects: List[SceneObject]) -> str:
        data = [self._serialize(obj) for obj in objects]
        return json.dumps(data, indent=2, ensure_ascii=False)

    def load(self, raw: str) -> List[SceneObject]:
        try:
            data = json.loads(raw)
            return [self._deserialize(item) for item in data]
        except Exception as e:
            logger.error(f"Falha crítica na deserialização da cena: {e}")
            raise

    def _serialize(self, obj: SceneObject) -> Dict[str, Any]:
        data = dataclasses.asdict(obj)
        data.pop("vtk_actor_ref", None)
        data.pop("mesh_data", None)
        return data

    def _deserialize(self, data: Dict[str, Any]) -> SceneObject:
        valid_fields = {f.name for f in dataclasses.fields(SceneObject)}

        clean_data = {k: v for k, v in data.items() if k in valid_fields}
        if "colors" in clean_data and isinstance(clean_data["colors"], list):
            clean_data["colors"] = tuple(clean_data["colors"])
        return SceneObject(**clean_data)