from __future__ import annotations
from core.components.tools.base.base_tool import BaseTool
from core.components.tools.base.base_tool import InteractionContext
from core.localization.translator import tr

class ResetViewTool(BaseTool):
    name: str = "reset_view"
    display_name: str = tr("toolbar.reset_view", "Resetar Vista")
    icon: str = "home.svg"
    tool_tip: str = tr("toolbar.reset_view_tooltip", "Resetar a câmera para a posição inicial")

    def on_activate(self) -> None:
        if self.context and self.context.renderer:
            self.context.renderer.ResetCamera()
            self.render()
        self.deactivate()

    def activate(self, context: InteractionContext) -> None:
        super().activate(context)