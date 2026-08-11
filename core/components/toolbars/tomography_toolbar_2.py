import sys
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_toolbar.base_toolbar import BaseToolbar, AppContext

# Tools
from core.components.tools.volume.dicom.load_dicom_tool import LoadDicomTool
from core.components.tools.volume.dicom.save_vti_tool import SaveVtiTool
from core.components.tools.volume.dicom.layout_dicom_tool import LayoutDicomTool
from core.components.tools.volume.dicom.reset_dicom_tool import ResetDicomTool
from core.components.tools.volume.vizualizations.color_map_tool import ColorMapTool


class TomographyToolbar(BaseToolbar):
    layoutChanged = QtCore.Signal(str)

    def __init__(self, app_context: AppContext, parent=None):
        super().__init__("Tomografia", app_context, parent)
        self._validation_state = False

    def setup_ui(self):
        tool_classes = [LoadDicomTool, SaveVtiTool, LayoutDicomTool, ResetDicomTool, ColorMapTool]
        tool_keys = [tool.name for tool in tool_classes]

        # Garante que as ferramentas estejam registradas no tool_manager se ele suportar
        if self.tool_manager and hasattr(self.tool_manager, "register_tool"):
            for tool_class in tool_classes:
                try:
                    # Verifica se já não existe para evitar sobrescrever instâncias com estado
                    if not self.tool_manager.get_tool(tool_class.name):
                        self.tool_manager.register_tool(tool_class.name, tool_class())
                except Exception:
                    pass

        # Adiciona os widgets/ações correspondentes na toolbar
        for key in tool_keys:
            tool = self.tool_manager.get_tool(key) if self.tool_manager else None

            # Fallback robusto caso o gerenciador não retorne
            if not tool:
                if key == LoadDicomTool.name:
                    tool = LoadDicomTool()
                elif key == SaveVtiTool.name:
                    tool = SaveVtiTool()
                elif key == LayoutDicomTool.name:
                    tool = LayoutDicomTool()
                elif key == ResetDicomTool.name:
                    tool = ResetDicomTool()
                elif key == ColorMapTool.name:
                    tool = ColorMapTool()

            if tool:
                self.register_tool(tool)

        # Atualiza o estado inicial das ferramentas dependentes de validação
        self._update_tools_availability()

    def set_validation_state(self, state: bool):
        """Método chamado pelo módulo/pipeline para indicar que o DICOM foi validado e carregado."""
        self._validation_state = state
        self._update_tools_availability()

    def _update_tools_availability(self):
        """Habilita ou desabilita ferramentas dependentes de tomografia carregada."""
        dependent_tools = [SaveVtiTool.name, LayoutDicomTool.name, ResetDicomTool.name, ColorMapTool.name]

        for key in dependent_tools:
            tool = self.tool_manager.get_tool(key) if self.tool_manager else None
            if tool and hasattr(tool, "setEnabled"):
                tool.setEnabled(self._validation_state)

    def _on_layout_changed(self, text):
        if self.tool_manager:
            tool = self.tool_manager.get_tool(LayoutDicomTool.name) or self.tool_manager.get_tool("layout")
            if tool and hasattr(tool, "apply_layout"):
                tool.apply_layout(text)
        self.layoutChanged.emit(text)


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