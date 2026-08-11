from __future__ import annotations

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

        # Geometria genérica (preenchida via duck typing)
        self._dimensions: Tuple[int, int, int] = (0, 0, 0)
        self._spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
        self._origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)

        self._extract_geometry()

    def _extract_geometry(self):
        """Tenta extrair propriedades geométricas usando métodos comuns (Duck Typing),
        evitando acoplamento estrito com o VTK ou ITK.
        """
        try:
            if hasattr(self._image_data, "GetDimensions"):
                self._dimensions = tuple(self._image_data.GetDimensions())
                self._spacing = tuple(self._image_data.GetSpacing())
                self._origin = tuple(self._image_data.GetOrigin())
                return
        except Exception:
            pass

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
        return self._image_data is not None and all(dim > 0 for dim in self._dimensions)

    def get_voxel_count(self) -> int:
        if not self.is_valid:
            return 0
        return self._dimensions[0] * self._dimensions[1] * self._dimensions[2]

    def get_physical_size(self) -> Tuple[float, float, float]:
        if not self.is_valid:
            return (0.0, 0.0, 0.0)
        return (
            self._dimensions[0] * self._spacing[0],
            self._dimensions[1] * self._spacing[1],
            self._dimensions[2] * self._spacing[2]
        )

    def __repr__(self) -> str:
        return (
            f"Volume("
            f"name='{self.name}', "
            f"dimensions={self.dimensions}, "
            f"spacing={self.spacing}, "
            f"source={self.source_path})"
        )