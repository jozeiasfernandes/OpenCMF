import vtk
from core.tools.base.base_tool import BaseTool


class MoveTool(BaseTool):
    name = "move"
    display_name = "Mover Objeto"
    cursor = None

    def __init__(self):
        super().__init__()
        self.target_actor = None
        self.last_pos = None

    def mouse_press(self, x: int, y: int, button: str, modifiers=None) -> bool:
        if button != "left":
            return False
        self.target_actor = self.get_picker_actor(x, y)
        if self.target_actor:
            self.last_pos = self.get_picker_position(x, y)
            return True

        return False

    def mouse_move(self, x: int, y: int, modifiers=None) -> bool:
        if not self.target_actor or not self.last_pos:
            return False
        current_pos = self.get_picker_position(x, y)
        if not current_pos:
            return False
        dx = current_pos[0] - self.last_pos[0]
        dy = current_pos[1] - self.last_pos[1]
        dz = current_pos[2] - self.last_pos[2]
        obj = self.context.scene_manager.get_object(getattr(self.target_actor, "id", None))
        if obj:
            self.context.scene_manager.transform_manager.translate(obj, dx, dy, dz)
            self.last_pos = current_pos
            self.render()
            return True
        return False

    def mouse_release(self, x: int, y: int, button: str, modifiers=None) -> bool:
        self.target_actor = None
        self.last_pos = None
        return True