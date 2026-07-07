from pathlib import Path
from typing import List, Iterable, Optional, Union
from .serializer import Serializer
from ..scene_object import SceneObject

class ScenePersistence:
    def __init__(self, serializer: Serializer):
        self._serializer = serializer

    def save_to_file(self, path: Union[str, Path], objects: Iterable[SceneObject]) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        json_content = self._serializer.save(list(objects))
        file_path.write_text(json_content, encoding="utf-8")

    def load_from_file(self, path: Union[str, Path]) -> List[SceneObject]:
        file_path = Path(path)
        if not file_path.exists():
            return []
        content = file_path.read_text(encoding="utf-8")
        return self._serializer.load(content)