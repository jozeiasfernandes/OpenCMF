import sys
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_toolbar.base_toolbar import BaseToolbar, AppContext

# Ferramentas
from domain.volume.visualization.lut.lut_presets import LUTPresets
from core.components.tools.volume.dicom.save_vti_tool import SaveVtiTool


class TomographyToolbar(BaseToolbar):
    lutChanged = QtCore.Signal(str)
    layoutChanged = QtCore.Signal(str)

    def __init__(self, app_context: AppContext, parent=None):
        super().__init__("Tomografia", app_context, parent)

        self._validation_state = False

    def setup_ui(self):

        self.btn_load = QtWidgets.QPushButton("⌛ Load Volume")
        self.addWidget(self.btn_load)

        self.add_separator()

        if self.tool_manager and hasattr(self.tool_manager, "register_tool"):
            try:
                self.tool_manager.register_tool("save_vti", SaveVtiTool())
            except TypeError:
                # Caso a assinatura espere apenas a instância (ex: register_tool(tool))
                try:
                    self.tool_manager.register_tool(SaveVtiTool())
                except Exception:
                    pass

        tool_keys = ["open", "validate", "save", "save_vti", "reset"]

        for key in tool_keys:
            tool = self.tool_manager.get_tool(key) if self.tool_manager else None
            if not tool and key == "save_vti":
                # Fallback direto caso o tool_manager não tenha a ferramenta cadastrada no ambiente de teste
                tool = SaveVtiTool()

            if tool:
                self.register_tool(tool)

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
        if self.tool_manager:
            tool = self.tool_manager.get_tool("layout")
            if tool and hasattr(tool, "apply_layout"):
                tool.apply_layout(text)
        self.layoutChanged.emit(text)

    def _on_lut_changed(self, text):
        if self.tool_manager:
            tool = self.tool_manager.get_tool("colors")
            if tool and hasattr(tool, "apply_lut"):
                tool.apply_lut(text)
        self.lutChanged.emit(text)


if __name__ == "__main__":
    class MockToolManager:
        def __init__(self):
            self.tools = {}

        def get_tool(self, key):
            return self.tools.get(key)

        def register_tool(self, *args):
            if len(args) == 2:
                self.tools[args[0]] = args[1]
            elif len(args) == 1:
                tool = args[0]
                if hasattr(tool, "name"):
                    self.tools[tool.name] = tool


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