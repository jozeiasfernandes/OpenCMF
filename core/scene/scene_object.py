import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

Vector3 = tuple[float, float, float]


@dataclass
class SceneObject:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = "Object"
    type: str = "generic"

    # Hierarquia (Scene Graph)
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)

    file_path: Optional[str] = None
    visible: bool = True
    opacity: float = 1.0
    color: Vector3 = (1.0, 1.0, 1.0)

    transforms: Dict[str, Vector3] = field(
        default_factory=lambda: {
            "position": (0.0, 0.0, 0.0),
            "rotation": (0.0, 0.0, 0.0),
            "scale": (1.0, 1.0, 1.0),
        }
    )

    render: Dict[str, Any] = field(default_factory=dict)
    volume: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing: Dict[str, Any] = field(default_factory=lambda: {"filters": []})

    @property
    def position(self) -> Vector3:
        return self.transforms.get("position", (0.0, 0.0, 0.0))

    @position.setter
    def position(self, value: Vector3):
        self.transforms["position"] = value

    @property
    def rotation(self) -> Vector3:
        return self.transforms.get("rotation", (0.0, 0.0, 0.0))

    @rotation.setter
    def rotation(self, value: Vector3):
        self.transforms["rotation"] = value

    @property
    def scale(self) -> Vector3:
        return self.transforms.get("scale", (1.0, 1.0, 1.0))

    @scale.setter
    def scale(self, value: Vector3):
        self.transforms["scale"] = value