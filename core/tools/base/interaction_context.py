from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import vtk


@dataclass(slots=True)
class InteractionContext:
    renderer: vtk.vtkRenderer
    interactor: vtk.vtkRenderWindowInteractor

    scene_manager: Optional[Any] = None
    event_bus: Optional[Any] = None
    window: Optional[Any] = None

    actor_registry: Optional[Any] = None
    object_registry: Optional[Any] = None
    selection_manager: Optional[Any] = None

    camera_controller: Optional[Any] = None
    command_manager: Optional[Any] = None

    def render(self) -> None:
        render_window = self.interactor.GetRenderWindow()

        if render_window:
            render_window.Render()