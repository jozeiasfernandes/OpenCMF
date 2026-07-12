import vtk
from PySide6 import QtCore
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory

class SelectTool(BaseTool):
    # Metadados para a interface
    name = "select"
    display_name = "Selecionar"
    category = ToolCategory.SELECTION
    icon = ":/icons/select.png"
    tool_tip = "Selecione objetos na cena. Use CTRL + Clique para seleção múltipla."

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

        self.picker.Pick(x, y, 0, self.context.renderer)
        actor = self.picker.GetActor()
        selection = self.context.scene_manager.selection

        if actor is None or not getattr(actor, "id", None):
            selection.clear()
            self.render()
            return True

        obj_id = actor.id
        ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier) if modifiers else False

        if ctrl_pressed:
            selection.toggle(obj_id)
        else:
            selection.select(obj_id, exclusive=True)

        self.render()
        return True