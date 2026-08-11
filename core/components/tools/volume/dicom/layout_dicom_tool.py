from __future__ import annotations

from PySide6 import QtWidgets, QtGui
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory


class LayoutDicomTool(BaseTool):
    name: str = "layout_dicom_tool"
    display_name: str = "Layout"
    category = ToolCategory.TOMOGRAPHY
    icon: str = "4_viewer.svg"
    tool_tip: str = "Altera o layout das janelas de visualização"

    toolbar_label: str = "Layout:"  # Adiciona o rótulo automaticamente via BaseToolbar

    LAYOUT_OPTIONS = [
        ("4 Quadrantes", "4_viewer.svg"),
        ("3D Only", "1_3d_viewer.svg"),
        ("Axial", "axial.svg"),
        ("Sagittal", "sagital.svg"),
        ("Coronal", "coronal.svg")
    ]

    def __init__(self):
        super().__init__()
        self.combo_widget: QtWidgets.QComboBox | None = None

    def create_widget(self) -> QtWidgets.QWidget:
        """Retorna diretamente o QComboBox configurado para a toolbar."""
        self.combo_widget = QtWidgets.QComboBox()
        for label, icon_name in self.LAYOUT_OPTIONS:
            icon = QtGui.QIcon(icon_name) if icon_name else QtGui.QIcon()
            self.combo_widget.addItem(icon, label, label)

        self.combo_widget.currentTextChanged.connect(self.apply_layout)
        return self.combo_widget

    def apply_layout(self, layout_name: str) -> None:
        if self.context and hasattr(self.context, "event_bus"):
            self.context.event_bus.emit(
                "LAYOUT_CHANGED",
                layout=layout_name
            )
        else:
            print(f"Layout solicitado: {layout_name} (EventBus não disponível)")