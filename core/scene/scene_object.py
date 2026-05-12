'''

SceneObject
├── id
├── name
├── type
├── visible
├── opacity
├── color
├── transform
├── metadata
├── file_path
└── vtk_actor_ref

'''
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple


@dataclass
class SceneObject:
    id: str
    name: str = "Object"
    type: str = "generic"

    visible: bool = True
    opacity: float = 1.0
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    transform: Dict[str, list[float]] = field(default_factory=lambda: {
        "position": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
    })

    metadata: Dict[str, Any] = field(default_factory=dict)
    mesh_data: Optional[Any] = None
    file_path: Optional[str] = None
    vtk_actor_ref: Optional[Any] = None

    def set_position(self, x: float, y: float, z: float):
        self.transform["position"] = [x, y, z]

    def set_rotation(self, x: float, y: float, z: float):
        self.transform["rotation"] = [x, y, z]

    def set_scale(self, x: float, y: float, z: float):
        self.transform["scale"] = [x, y, z]