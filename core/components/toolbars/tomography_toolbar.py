from __future__ import annotations

from core.components.bases.base_toolbar import BaseToolbar
from core.scene.scene_manager import SceneManager

# Ferramentas
from core.components.tools.open_dicom_tool import OpenDicomTool
from core.components.tools.reset_dicom_tool import ResetDicomTool
from core.components.tools.save_vti_tool import SaveVtiTool
from core.components.tools.validate_dicom_tool import ValidateDicomTool
from core.components.tools.layout_dicom_tool import LayoutDicomTool
from core.components.tools.color_map_tool import ColorMapTool
from core.volume.lookup_table.lut_presets import LUTPresets


class TomographyToolbar(BaseToolbar):
    def __init__(self, context, parent=None):
        # Call parent constructor with context as first argument
        super().__init__(context, "Tomografia", parent)

        # Instanciação das ferramentas
        self.tools = {
            "open": OpenDicomTool(),
            "validate": ValidateDicomTool(),
            "save": SaveVtiTool(),
            "reset": ResetDicomTool(),
            "layout": LayoutDicomTool(),
            "color": ColorMapTool(),
        }

        # Injeta o contexto em todas as ferramentas
        for tool in self.tools.values():
            tool.context = context

    def setup_ui(self):
        from PySide6 import QtWidgets

        self.add_tool_button("📁 Open", self.tools["open"].on_activate)
        self.add_tool_button("🔍 Validate", self.tools["validate"].on_activate)

        self.btn_load = QtWidgets.QPushButton("⌛ Load Volume")
        self.addWidget(self.btn_load)

        self.add_tool_button("💾 Save", self.tools["save"].on_activate)
        self.add_tool_button("🔄 Reset", self.tools["reset"].on_activate)

        self.addSeparator()

        # Layout
        self.addWidget(QtWidgets.QLabel("Layout:"))
        self.combo_layout = QtWidgets.QComboBox()
        self.combo_layout.addItems(["4 Quadrantes", "3D", "Axial", "Sagital", "Coronal"])
        self.combo_layout.currentTextChanged.connect(self.tools["layout"].apply_layout)
        self.addWidget(self.combo_layout)

        # Color Map (LUT)
        self.addWidget(QtWidgets.QLabel("LUT:"))
        self.combo_color = QtWidgets.QComboBox()
        self.combo_color.addItems(list(LUTPresets.PRESETS.keys()))
        self.combo_color.currentTextChanged.connect(self.tools["color"].apply_lut)
        self.addWidget(self.combo_color)


if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Debug Toolbar: Tomografia")
    window.resize(600, 100)


    class ContextMock:
        def __init__(self):
            self.scene_manager = SceneManager(None, None, None, None, None, None)  # Simplificado para teste


    my_context = ContextMock()

    toolbar = TomographyToolbar(context=my_context)
    window.addToolBar(toolbar)

    window.show()
    sys.exit(app.exec())