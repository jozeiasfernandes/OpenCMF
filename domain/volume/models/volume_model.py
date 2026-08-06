from pathlib import Path
from typing import Any, Optional, Tuple, Union


class Volume:
    """Representa um volume tridimensional de forma agnóstica a bibliotecas (VTK, ITK, NumPy)."""

    def __init__(
            self,
            image_data: Any,
            source_path: Optional[Union[str, Path]] = None,
            name: str = "Volume TC"
    ):
        if image_data is None:
            raise ValueError("image_data não pode ser None.")

        self._image_data: Any = image_data
        self.source_path: Optional[Path] = Path(source_path) if source_path else None
        self.name: str = name

        # Geometria genérica (pode ser preenchida por adaptadores ou duck typing)
        self._dimensions: Tuple[int, int, int] = (0, 0, 0)
        self._spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
        self._origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)

        self._extract_geometry()

    def _extract_geometry(self):
        """Tenta extrair propriedades geométricas usando métodos comuns (Duck Typing),
        evitando importar ou checar tipos específicos do VTK ou ITK aqui dentro.
        """
        try:
            # Compatível com vtkImageData
            if hasattr(self._image_data, "GetDimensions"):
                self._dimensions = tuple(self._image_data.GetDimensions())
                self._spacing = tuple(self._image_data.GetSpacing())
                self._origin = tuple(self._image_data.GetOrigin())
                return
        except Exception:
            pass

        # Aqui você também poderia adicionar suporte nativo a ITK ou NumPy se necessário no futuro
        # Ex: if 'itk' in type(self._image_data).__module__: ...

    @property
    def image_data(self) -> Any:
        return self._image_data

    @image_data.setter
    def image_data(self, data: Any):
        if data is None:
            raise ValueError("O novo dado de imagem não pode ser None.")
        self._image_data = data
        self._extract_geometry()

    @property
    def dimensions(self) -> Tuple[int, int, int]:
        return self._dimensions

    @property
    def spacing(self) -> Tuple[float, float, float]:
        return self._spacing

    @property
    def origin(self) -> Tuple[float, float, float]:
        return self._origin

    @property
    def is_valid(self) -> bool:
        return self._image_data is not None and sum(self._dimensions) > 0

    def get_voxel_count(self) -> int:
        if self.is_valid:
            return self._dimensions[0] * self._dimensions[1] * self._dimensions[2]
        return 0

    def get_physical_size(self) -> Tuple[float, float, float]:
        if self.is_valid:
            return (
                self._dimensions[0] * self._spacing[0],
                self._dimensions[1] * self._spacing[1],
                self._dimensions[2] * self._spacing[2]
            )
        return (0.0, 0.0, 0.0)

    def __repr__(self) -> str:
        return (
            f"Volume("
            f"name='{self.name}', "
            f"dimensions={self.dimensions}, "
            f"spacing={self.spacing}, "
            f"source={self.source_path})"
        )