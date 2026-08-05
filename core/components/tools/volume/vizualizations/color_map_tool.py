from __future__ import annotations
from typing import Any
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory
from core.volume.visualization.lut.lut_presets import LUTPresets

class ColorMapTool(BaseTool):
    name: str = "color_map_tool"
    display_name: str = "Color Map"
    category = ToolCategory.TOMOGRAPHY
    icon: str = "color_map.png"
    tool_tip: str = "Altera o mapa de cores do volume selecionado"

    def __init__(self):
        super().__init__()
        self._current_lut = "Default"

    def on_activate(self) -> None:
        pass

    def apply_lut(self, lut_name: str) -> None:
        if not self.context or not self.context.scene_manager:
            return

        if lut_name in LUTPresets.PRESETS:
            self._current_lut = lut_name
            self.context.scene_manager.set_color_map(lut_name)
            self.render()
        else:
            print(f"Aviso: Preset '{lut_name}' não encontrado.")

    def wheel_forward(self, x: int, y: int, modifiers: Any = None) -> bool:
        self._cycle_lut(direction=1)
        return True

    def wheel_backward(self, x: int, y: int, modifiers: Any = None) -> bool:
        self._cycle_lut(direction=-1)
        return True

    def _cycle_lut(self, direction: int):
        presets = list(LUTPresets.PRESETS.keys())
        if self._current_lut in presets:
            idx = presets.index(self._current_lut)
            new_idx = (idx + direction) % len(presets)
            new_lut = presets[new_idx]
            self.apply_lut(new_lut)


if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    tool = ColorMapTool()
    print(f"Ferramenta inicializada: {tool.display_name}")
    print(f"Presets disponíveis: {list(LUTPresets.PRESETS.keys())}")

    tool._current_lut = "Default"
    tool._cycle_lut(1)
    print(f"Nova LUT após scroll: {tool._current_lut}")

    # Se você quiser apenas validar se a classe está correta:
    print("ColorMapTool carregada com sucesso.")