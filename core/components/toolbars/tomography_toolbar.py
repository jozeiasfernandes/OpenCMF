from PySide6 import QtCore, QtWidgets

from core.components.bases.base_toolbar import BaseToolbar, ToolData
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

    def __init__(self, context, parent=None):
        super().__init__(context, "Tomografia", parent)

        self._validation_state = False

        self.tools = {
            "open": OpenDicomTool(),
            "validate": ValidateDicomTool(),
            "save": SaveVtiTool(),
            "reset": ResetDicomTool(),
            "layout": LayoutDicomTool(),
            "color": ColorMapTool(),
        }

        for tool in self.tools.values():
            tool.context = context

        self.setup_ui()

    def setup_ui(self):
        # 1. Ajuste dos botões de ferramenta
        tools_config = [
            ("open", "📁 Open", "Abrir arquivo DICOM"),
            ("validate", "🔍 Validate", "Validar arquivos DICOM"),
            ("save", "💾 Save", "Salvar volume .vti"),
            ("reset", "🔄 Reset", "Resetar visualização")
        ]

        for key, display, tooltip in tools_config:
            self.add_tool_button(ToolData(
                name=key,
                display_name=display,
                icon_path=None,
                tool_tip=tooltip,
                callback=self.tools[key].on_activate
            ))

        self.addSeparator()

        # 2. Botão de carga
        self.btn_load = QtWidgets.QPushButton("⌛ Load Volume")
        self.addWidget(self.btn_load)

        self.addSeparator()

        # 3. Layout (Widget de controle com sinal)
        self.addWidget(QtWidgets.QLabel("Layout:"))
        self.combo_layout = QtWidgets.QComboBox()
        self.combo_layout.addItems(["4 Quadrantes", "3D", "Axial", "Sagital", "Coronal"])
        # Conectado ao método ponte
        self.combo_layout.currentTextChanged.connect(self._on_layout_changed)
        self.addWidget(self.combo_layout)

        # 4. Color Map (Widget de controle com sinal)
        self.addWidget(QtWidgets.QLabel("LUT:"))
        self.combo_color = QtWidgets.QComboBox()
        self.combo_color.addItems(list(LUTPresets.PRESETS.keys()))
        # Conectado ao método ponte
        self.combo_color.currentTextChanged.connect(self._on_lut_changed)
        self.addWidget(self.combo_color)

    def set_validation_state(self, state: bool):
        """Método chamado pelo módulo para indicar que o DICOM foi validado."""
        self._validation_state = state

    def _on_layout_changed(self, text):
        self.tools["layout"].apply_layout(text)
        self.layoutChanged.emit(text)

    def _on_lut_changed(self, text):
        self.tools["color"].apply_lut(text)
        self.lutChanged.emit(text)


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