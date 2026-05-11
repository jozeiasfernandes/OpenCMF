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

    transform: Dict[str, Any] = field(default_factory=lambda: {
        "position": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
    })

    metadata: Dict[str, Any] = field(default_factory=dict)

    file_path: Optional[str] = None
    vtk_actor_ref: Any = None