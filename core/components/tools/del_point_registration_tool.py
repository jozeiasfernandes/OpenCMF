from core.components.tools.base.base_tool import BaseTool
from core.scene.events.scene_events import REGISTRATION_DELETE_LAST_MARKER

class DelPointRegistrationTool(BaseTool):
    name = "del_point"
    display_name = "Remover Ponto"
    icon = "del_point.svg"
    tool_tip = "Remove o último ponto de registro adicionado."

    def __init__(self):
        super().__init__()

    def activate(self, context) -> None:
        super().activate(context)
        if self.context and hasattr(self.context, 'event_bus'):
            self.context.event_bus.emit(REGISTRATION_DELETE_LAST_MARKER)
            print("Comando de remoção de ponto enviado.")
        self.deactivate()

    def mouse_press(self, x: int, y: int, button: str, modifiers=None) -> bool:
        return False