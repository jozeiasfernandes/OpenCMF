from __future__ import annotations
from typing import Any
from PySide6 import QtWidgets, QtGui

from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory
from domain.volume.visualization.lut.lut_presets import LUTPresets
from domain.volume.visualization.lut.lut_delegate import LUTDelegate
from core.application.scene.events.scene_events import VolumeEvents


class ColorMapTool(BaseTool):
    name: str = "color_map_tool"
    display_name: str = "Color Map"
    category = ToolCategory.TOMOGRAPHY
    icon: str = "color_map.png"
    tool_tip: str = "Altera o mapa de cores do volume selecionado"
    toolbar_label: str = "Color Map:"

    def __init__(self):
        super().__init__()
        self._current_lut = "Default"
        self.combo_widget: QtWidgets.QComboBox | None = None

    def create_widget(self) -> QtWidgets.QWidget:
        """Cria e retorna o QComboBox customizado para a toolbar."""
        self.combo_widget = QtWidgets.QComboBox()
        presets = list(LUTPresets.PRESETS.keys())
        for lut_name in presets:
            self.combo_widget.addItem(lut_name, lut_name)

        # Aplica o delegate que desenha o gradiente como fundo preenchido
        self.combo_widget.setItemDelegate(LUTDelegate())
        if self._current_lut in presets:
            self.combo_widget.setCurrentText(self._current_lut)

        self.combo_widget.currentTextChanged.connect(self.apply_lut)
        return self.combo_widget

    def on_activate(self) -> None:
        pass

    def apply_lut(self, lut_name: str) -> None:
        if lut_name in LUTPresets.PRESETS:
            self._current_lut = lut_name

            if self.combo_widget and self.combo_widget.currentText() != lut_name:
                self.combo_widget.setCurrentText(lut_name)

            if self.context and hasattr(self.context, "event_bus") and self.context.event_bus:
                # Uso da constante em vez de string mágica
                self.context.event_bus.emit(VolumeEvents.LUT_CHANGED, lut_name=lut_name)
            elif self.context and hasattr(self.context, "scene_manager") and self.context.scene_manager:
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

    app = QtWidgets.QApplication(sys.argv)

    tool = ColorMapTool()
    print(f"Ferramenta inicializada: {tool.display_name}")
    print(f"Presets disponíveis: {list(LUTPresets.PRESETS.keys())}")

    tool._current_lut = "Default"
    tool._cycle_lut(1)
    print(f"Nova LUT após scroll: {tool._current_lut}")
    print("ColorMapTool carregada com sucesso.")