from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory
from core.scene.events.scene_events import RegistrationEvents

class DelPointRegistrationTool(BaseTool):
    name = "del_point"
    display_name = "Remover Ponto"
    category = ToolCategory.REGISTRATION
    icon = "del_point.svg"
    tool_tip = "Remove o último ponto de registro adicionado."

    def __init__(self):
        super().__init__()

    def on_activate(self) -> None:
        super().on_activate()

        if self.context and hasattr(self.context, 'event_bus'):
            self.context.event_bus.emit(RegistrationEvents.DELETE_LAST_MARKER)
            print("[INFO] Comando de remoção de ponto enviado.")

        if self.context and hasattr(self.context, 'tool_manager'):
            self.context.tool_manager.deactivate_current_tool()

    def mouse_press(self, x: int, y: int, button: str, modifiers=None) -> bool:
        return False