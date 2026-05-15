from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Any

import vtk


@dataclass(slots=True)
class InteractionEvent:
    x: int
    y: int

    button: Optional[str] = None

    modifiers: Optional[Any] = None

    key: Optional[str] = None

    actor: Optional[vtk.vtkActor] = None

    picked_position: Optional[
        Tuple[float, float, float]
    ] = None

    consumed: bool = False

    def consume(self) -> None:
        self.consumed = True

    @property
    def has_actor(self) -> bool:
        return self.actor is not None

    @property
    def has_position(self) -> bool:
        return self.picked_position is not None