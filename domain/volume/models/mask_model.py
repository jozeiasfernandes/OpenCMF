from typing import Tuple
import vtk

from domain.volume.models.image_data import ImageData


class Mask(ImageData):
    """Representa uma máscara de segmentação."""

    def __init__(
        self,
        vtk_data: vtk.vtkImageData,
        name: str = "Máscara",
        color: Tuple[float, float, float] = (0.0, 1.0, 0.0),
        opacity: float = 0.6,
        label_id: int = 1,
    ):
        super().__init__(vtk_data)

        self.name = name
        self.label_id = label_id

        self.color = color
        self.opacity = opacity

        self.visible = True
        self.locked = False
        self.selected = False

    def __repr__(self):
        return (
            f"Mask(name='{self.name}', "
            f"label={self.label_id})"
        )