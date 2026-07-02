import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any


def default_transform() -> Dict:
    return {
        "position": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0]
    }


def default_render() -> Dict:
    return {
        "color": [1.0, 1.0, 1.0],
        "representation": "surface",
        "lighting": True,
        "ambient": 0.1,
        "diffuse": 0.7,
        "specular": 0.2,
        "specular_power": 10.0,
        "interpolation": "phong",
        "point_size": 1.0,
        "line_width": 1.0,
        "edge_visibility": False,
        "edge_color": [0.0, 0.0, 0.0],
        "backface_culling": False,
        "frontface_culling": False,
        "scalar_visibility": False,
        "scalar_mode": "point",
        "scalar_range": [0.0, 1.0],
        "lookup_table": "default",
        "color_map": {"preset": "grayscale", "invert": False},
        "texture": {"enabled": False, "file_path": ""}
    }


def default_volume() -> Dict:
    return {
        "spacing": [0.0, 0.0, 0.0],
        "dimensions": [0, 0, 0],
        "window_level": {"level": 0, "width": 0},
        "interpolation": "linear",
        "volume_rendering": {"enabled": False, "mode": "composite"},
        "transfer_function": {"color": [], "opacity": []}
    }


def default_metadata() -> Dict:
    now = datetime.now().isoformat()
    return {
        "created_at": now,
        "updated_at": now,
        "source": "import",
        "patient_id": "",
        "study_id": "",
        "modality": "",
        "date": "",
        "tags": []
    }


@dataclass
class ObjectProperties:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = ""
    file_path: str = ""
    format: str = ""

    visible: bool = True
    locked: bool = False
    selectable: bool = True
    opacity: float = 1.0

    transform: Dict = field(default_factory=default_transform)
    render: Dict = field(default_factory=default_render)
    volume: Dict = field(default_factory=default_volume)

    processing: Dict = field(
        default_factory=lambda: {"thresholds": [], "segmentation": {"method": "manual", "mask_path": ""},
                                 "filters": []})
    lod: Dict = field(default_factory=lambda: {"enabled": False, "decimation": 0.5})
    interaction: Dict = field(
        default_factory=lambda: {"draggable": True, "rotatable": True, "scalable": True, "pickable": True})

    clipping_planes: List[Dict] = field(default_factory=list)
    annotations: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=default_metadata)

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict):
        return cls(**data)