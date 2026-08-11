from typing import Tuple

import vtk


class ImageData:
    """Classe base para objetos que encapsulam um vtkImageData."""

    def __init__(self, vtk_data: vtk.vtkImageData):
        if vtk_data is None:
            raise ValueError("vtk_data não pode ser None.")

        self._vtk_data = vtk_data
        self._dimensions: Tuple[int, int, int] = (0, 0, 0)
        self._spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
        self._origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._extent: Tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0)
        self._center: Tuple[float, float, float] = (0.0, 0.0, 0.0)

        self._update_cache()

    def _update_cache(self):
        self._dimensions = tuple(self._vtk_data.GetDimensions())
        self._spacing = tuple(self._vtk_data.GetSpacing())
        self._origin = tuple(self._vtk_data.GetOrigin())
        self._extent = tuple(self._vtk_data.GetExtent())
        self._center = tuple(self._vtk_data.GetCenter())

    @property
    def vtk_data(self) -> vtk.vtkImageData:
        return self._vtk_data

    def update_image(self, vtk_data: vtk.vtkImageData):
        if vtk_data is None:
            raise ValueError("vtk_data não pode ser None.")
        self._vtk_data = vtk_data
        self._update_cache()

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
    def extent(self) -> Tuple[int, int, int, int, int, int]:
        return self._extent

    @property
    def center(self) -> Tuple[float, float, float]:
        return self._center

    @property
    def is_valid(self) -> bool:
        return (
                self._vtk_data is not None
                and isinstance(self._vtk_data, vtk.vtkImageData)
                and self._vtk_data.GetNumberOfPoints() > 0
        )