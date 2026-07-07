from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
import uuid


@dataclass
class SceneObject:
    """
    Representação única e unificada de um objeto na cena.
    Centraliza propriedades de estado, persistência e configuração de renderização.
    """
    # Identificação
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = "Object"
    type: str = "generic"  # "mesh", "volume", "dicom"

    # Persistência
    file_path: Optional[str] = None

    # Estado Visual
    visible: bool = True
    opacity: float = 1.0
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    # Transformações (Mantido com 's' para consistência com VTKPropertySync )
    transforms: Dict[str, List[float]] = field(
        default_factory=lambda: {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
        }
    )

    # Estruturas de Dados Consolidadas
    render: Dict[str, Any] = field(default_factory=dict)
    volume: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Processamento (adicionado conforme necessidade do core/objects_manager [cite: 2])
    processing: Dict[str, Any] = field(default_factory=lambda: {"filters": []})

    @property
    def position(self) -> List[float]:
        return self.transforms.get("position", [0.0, 0.0, 0.0])

    @position.setter
    def position(self, value: List[float]):
        self.transforms["position"] = value

    @property
    def rotation(self) -> List[float]:
        return self.transforms.get("rotation", [0.0, 0.0, 0.0])

    @rotation.setter
    def rotation(self, value: List[float]):
        self.transforms["rotation"] = value

    @property
    def scale(self) -> List[float]:
        return self.transforms.get("scale", [1.0, 1.0, 1.0])

    @scale.setter
    def scale(self, value: List[float]):
        self.transforms["scale"] = value