'''

SceneObject
├── id
├── name
├── type
├── visible
├── opacity
├── color
├── transforms
├── metadata
├── file_path
└── vtk_actor_ref

'''
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List

@dataclass
class SceneObject:
    # Identificadores e propriedades básicas
    id: str
    name: str = "Object"
    type: str = "generic"
    visible: bool = True
    opacity: float = 1.0
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    # Transformações (mantido no plural conforme estrutura definida)
    transforms: Dict[str, List[float]] = field(default_factory=lambda: {
        "position": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
    })

    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None

    # Referências externas (VTK/Mesh)
    mesh_data: Optional[Any] = None
    vtk_actor_ref: Optional[Any] = None