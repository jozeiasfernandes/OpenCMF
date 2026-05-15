from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

import vtk


@dataclass(slots=True)
class InteractionContext:
    renderer: vtk.vtkRenderer
    interactor: vtk.vtkRenderWindowInteractor
    scene_manager: Any = None
    window: Any = None
    event_bus: Any = None


class BaseTool:
    name = "base_tool"
    display_name = "Base Tool"
    cursor = None

    def __init__(self):
        self.context: Optional[InteractionContext] = None
        self.active = False

    def activate(self, context: InteractionContext) -> None:
        self.context = context
        self.active = True

        if self.cursor is not None and context.window is not None:
            context.window.setCursor(self.cursor)

        self.on_activate()

    def deactivate(self) -> None:
        if not self.context:
            return

        if self.context.window is not None:
            self.context.window.unsetCursor()

        self.on_deactivate()

        self.active = False
        self.context = None

    def on_activate(self) -> None:
        pass

    def on_deactivate(self) -> None:
        pass

    def mouse_press(
        self,
        x: int,
        y: int,
        button: str,
        modifiers: Any = None,
    ) -> bool:
        return False

    def mouse_move(
        self,
        x: int,
        y: int,
        modifiers: Any = None,
    ) -> bool:
        return False

    def mouse_release(
        self,
        x: int,
        y: int,
        button: str,
        modifiers: Any = None,
    ) -> bool:
        return False

    def wheel_forward(
        self,
        x: int,
        y: int,
        modifiers: Any = None,
    ) -> bool:
        return False

    def wheel_backward(
        self,
        x: int,
        y: int,
        modifiers: Any = None,
    ) -> bool:
        return False

    def key_press(
        self,
        key: str,
        modifiers: Any = None,
    ) -> bool:
        return False

    def key_release(
        self,
        key: str,
        modifiers: Any = None,
    ) -> bool:
        return False

    def render(self) -> None:
        if not self.context:
            return

        render_window = self.context.interactor.GetRenderWindow()

        if render_window:
            render_window.Render()

    def get_picker_actor(self, x: int, y: int):
        if not self.context:
            return None

        picker = vtk.vtkPropPicker()

        picker.Pick(
            x,
            y,
            0,
            self.context.renderer
        )

        return picker.GetActor()

    def get_picker_position(self, x: int, y: int):
        if not self.context:
            return None

        picker = vtk.vtkPointPicker()

        picker.Pick(
            x,
            y,
            0,
            self.context.renderer
        )

        return picker.GetPickPosition()