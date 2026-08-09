from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory

class ScaleTool(BaseTool):
    name = "scale"
    display_name = "Escalar Objeto"
    category = ToolCategory.TRANSFORMATION
    icon = ":/icons_manager/scale.png"
    tool_tip = "Clique e arraste para alterar a escala do objeto."

    def __init__(self):
        super().__init__()
        self.target_actor = None
        self.last_y = 0

    def mouse_press(self, x: int, y: int, button: str, modifiers=None) -> bool:
        if button != "left":
            return False
        self.target_actor = self.get_picker_actor(x, y)
        if self.target_actor:
            self.last_y = y
            return True
        return False

    def mouse_move(self, x: int, y: int, modifiers=None) -> bool:
        if not self.target_actor:
            return False
        delta_y = y - self.last_y
        scale_factor = 1.0 + (delta_y * 0.01)
        if scale_factor < 0.1:
            scale_factor = 0.1
        obj_id = getattr(self.target_actor, "id", None)
        obj = self.context.scene_manager.objects.get(obj_id)
        if obj:
            self.context.scene_manager.transform_manager.scale(
                obj,
                scale_factor,
                scale_factor,
                scale_factor
            )
            self.last_y = y
            self.render()
            return True
        return False

    def mouse_release(self, x: int, y: int, button: str, modifiers=None) -> bool:
        self.target_actor = None
        return True