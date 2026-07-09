from __future__ import annotations
from core.components.tools.base.base_tool import BaseTool, ToolCategory


class ResetDicomTool(BaseTool):
    name: str = "reset_view"
    display_name: str = "Resetar Visualização"
    category: ToolCategory = ToolCategory.VIEWER

    def on_activate(self) -> None:
        self.reset_scene()
        self.deactivate()

    def reset_scene(self) -> None:
        if not self.context or not self.context.renderer:
            print("Erro: Contexto ou Renderer não disponível.")
            return

        self.context.renderer.ResetCamera()

        if self.context.scene_manager:
            self.context.scene_manager.reset_window_level()
            self.context.scene_manager.reset_camera_clipping_planes()

        self.render()
        print("Cena resetada para as configurações originais.")

    def on_deactivate(self) -> None:
        pass