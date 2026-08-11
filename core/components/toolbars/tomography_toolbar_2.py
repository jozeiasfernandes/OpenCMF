import sys
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_toolbar.base_toolbar import BaseToolbar, AppContext

# Tools

from core.components.tools.volume.dicom.save_vti_tool import SaveVtiTool
from core.components.tools.volume.dicom.layout_dicom_tool import LayoutDicomTool
from core.components.tools.volume.dicom.load_dicom_tool import LoadDicomTool
from core.components.tools.volume.dicom.reset_dicom_tool import ResetDicomTool
from core.components.tools.volume.vizualizations.color_map_tool import ColorMapTool

from domain.volume.visualization.lut.lut_presets import LUTPresets




class TomographyToolbar(BaseToolbar):
    lutChanged = QtCore.Signal(str)
    layoutChanged = QtCore.Signal(str)

    def __init__(self, app_context: AppContext, parent=None):
        super().__init__("Tomografia", app_context, parent)

        self._validation_state = False

    def setup_ui(self):
        if self.tool_manager and hasattr(self.tool_manager, "register_tool"):
            try:
                self.tool_manager.register_tool(LoadDicomTool.name, LoadDicomTool())
            except TypeError:
                try:
                    self.tool_manager.register_tool(LoadDicomTool())
                except Exception:
                    pass

            try:
                self.tool_manager.register_tool(SaveVtiTool.name, SaveVtiTool())
            except TypeError:
                try:
                    self.tool_manager.register_tool(SaveVtiTool())
                except Exception:
                    pass

            try:
                self.tool_manager.register_tool(LayoutDicomTool.name, LayoutDicomTool())
            except TypeError:
                try:
                    self.tool_manager.register_tool(LayoutDicomTool())
                except Exception:
                    pass

            try:
                self.tool_manager.register_tool(ResetDicomTool.name, ResetDicomTool())
            except TypeError:
                try:
                    self.tool_manager.register_tool(ResetDicomTool())
                except Exception:
                    pass

            try:
                self.tool_manager.register_tool(ColorMapTool.name, ColorMapTool())
            except TypeError:
                try:
                    self.tool_manager.register_tool(ColorMapTool())
                except Exception:
                    pass

        tool_keys = [
            LoadDicomTool.name,
            SaveVtiTool.name,
            LayoutDicomTool.name,
            ResetDicomTool.name,
            ColorMapTool.name
        ]

        for key in tool_keys:
            tool = self.tool_manager.get_tool(key) if self.tool_manager else None
            if not tool and key == LoadDicomTool.name:
                tool = LoadDicomTool()
            elif not tool and key == SaveVtiTool.name:
                tool = SaveVtiTool()
            elif not tool and key == LayoutDicomTool.name:
                tool = LayoutDicomTool()
            elif not tool and key == ResetDicomTool.name:
                tool = ResetDicomTool()
            elif not tool and key == ColorMapTool.name:
                tool = ColorMapTool()

            if tool:
                self.register_tool(tool)

        self.add_separator()


    def set_validation_state(self, state: bool):
        """Método chamado pelo módulo para indicar que o DICOM foi validado."""
        self._validation_state = state

    def _on_layout_changed(self, text):
        if self.tool_manager:
            tool = self.tool_manager.get_tool(LayoutDicomTool.name) or self.tool_manager.get_tool("layout")
            if tool and hasattr(tool, "apply_layout"):
                tool.apply_layout(text)
        self.layoutChanged.emit(text)

    def _on_lut_changed(self, text):
        if self.tool_manager:
            tool = self.tool_manager.get_tool(ColorMapTool.name) or self.tool_manager.get_tool("colors")
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

        def activate_tool(self, tool):
            if hasattr(tool, "on_activate"):
                tool.on_activate()


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