from dataclasses import dataclass, field


@dataclass
class SceneObject:
    id: str
    name: str
    type: str  # "mesh", "volume", "dicom"

    # Dados de arquivo
    file_path: str = ""

    # Estado (O que o usuário vê)
    visible: bool = True
    opacity: float = 1.0

    # Dados estruturados
    transform: dict = field(default_factory=default_transform)
    render: dict = field(default_factory=default_render)
    volume: dict = field(default_factory=default_volume)
    metadata: dict = field(default_factory=default_metadata)

    # Apenas o essencial para processamento
    processing: dict = field(default_factory=lambda: {"filters": []})