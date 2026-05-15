'''
Mouse Click
    ↓
SelectTool
    ↓
vtk picker
    ↓
SelectionManager
    ↓
SELECTION_CHANGED
    ↓
views update

'''

import vtk

from PySide6 import QtCore

from core.tools import BaseTool


class SelectTool(BaseTool):
    name = "select"
    display_name = "Select"

    def __init__(self):
        super().__init__()

        self.picker = vtk.vtkPropPicker()

    def mouse_press(
        self,
        x: int,
        y: int,
        button: str,
        modifiers=None,
    ) -> bool:
        if button != "left":
            return False

        if not self.context:
            return False

        self.picker.Pick(
            x,
            y,
            0,
            self.context.renderer
        )

        actor = self.picker.GetActor()

        selection = self.context.scene_manager.selection

        if actor is None:
            selection.clear()
            self.render()
            return True

        obj_id = getattr(actor, "id", None)

        if not obj_id:
            selection.clear()
            self.render()
            return True

        ctrl_pressed = False

        if modifiers is not None:
            ctrl_pressed = bool(
                modifiers & QtCore.Qt.ControlModifier
            )

        if ctrl_pressed:
            selection.toggle(obj_id)
        else:
            selection.select(
                obj_id,
                exclusive=True
            )

        self.render()

        return True