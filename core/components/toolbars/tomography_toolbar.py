import sys
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_toolbar import BaseToolbar, ToolData, AppContext
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
    lutChanged = QtCore.Signal(str)
    layoutChanged = QtCore.Signal(str)

    def __init__(self, app_context: AppContext, parent=None):
        super().__init__("Tomografia", app_context, parent)

        self._validation_state = False

        self.initialize()

    def setup_ui(self):
        tool_keys = ["open", "validate", "save", "reset"]

        for key in tool_keys:
            tool = self.tool_manager.get_tool(key)
            if tool:
                self.register_tool(tool)

        self.add_separator()

        self.btn_load = QtWidgets.QPushButton("⌛ Load Volume")
        self.addWidget(self.btn_load)

        self.add_separator()


        self.addWidget(QtWidgets.QLabel("Layout:"))
        self.combo_layout = QtWidgets.QComboBox()
        self.combo_layout.addItems(["4 Quadrantes", "3D", "Axial", "Sagital", "Coronal"])
        self.combo_layout.currentTextChanged.connect(self._on_layout_changed)
        self.addWidget(self.combo_layout)


        self.addWidget(QtWidgets.QLabel("LUT:"))
        self.combo_color = QtWidgets.QComboBox()

        self.combo_color.addItems(list(LUTPresets.PRESETS.keys()))
        self.combo_color.currentTextChanged.connect(self._on_lut_changed)
        self.addWidget(self.combo_color)

    def set_validation_state(self, state: bool):
        """Método chamado pelo módulo para indicar que o DICOM foi validado."""
        self._validation_state = state

    def _on_layout_changed(self, text):
        tool = self.tool_manager.get_tool("layout")
        if tool:
            tool.apply_layout(text)
        self.layoutChanged.emit(text)

    def _on_lut_changed(self, text):
        tool = self.tool_manager.get_tool("color")
        if tool:
            tool.apply_lut(text)
        self.lutChanged.emit(text)


if __name__ == "__main__":
    class MockToolManager:
        def get_tool(self, key): return None # Retorne um objeto mockado se necessário

    class MockSceneManager:
        pass

    class MockSettings:
        def get(self, key, default=None): return None
        def set(self, key, value): pass

    my_context = AppContext(
        tool_manager=MockToolManager(),
        scene_manager=MockSceneManager(),
        settings=MockSettings()
    )

    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Debug Toolbar: Tomografia")
    window.resize(600, 100)


    toolbar = TomographyToolbar(app_context=my_context)
    window.addToolBar(toolbar)

    window.show()
    sys.exit(app.exec())