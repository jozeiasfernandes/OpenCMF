from __future__ import annotations
from typing import Any
from core.components.tools.base.base_tool import BaseTool, ToolCategory
from core.scene.events.scene_events import SceneEvents

class LayoutDicomTool(BaseTool):
    name: str = "layout_dicom_tool"
    display_name: str = "Layout"
    category = ToolCategory.TOMOGRAPHY
    icon: str = "layout.png"
    tool_tip: str = "Altera o layout das janelas de visualização"

    def __init__(self):
        super().__init__()

    def apply_layout(self, layout_name: str) -> None:
        if self.context and hasattr(self.context, "event_bus"):
            self.context.event_bus.emit(
                SceneEvents.INTERACTION_MODE_CHANGED,
                layout=layout_name
            )
        else:
            print(f"Layout solicitado: {layout_name} (EventBus não disponível)")