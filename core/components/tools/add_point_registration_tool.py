import vtk
from PySide6 import QtWidgets, QtCore, QtGui
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory
from list_paths import ICONS_DIR
from core.scene.events.scene_events import RegistrationEvents

class AddPointRegistrationTool(BaseTool):
    name = "add_point"
    display_name = "Adicionar Pontos"
    category = ToolCategory.REGISTRATION
    icon = "add_point.svg"
    tool_tip = "Clique na superfície do objeto para adicionar um ponto de registro."

    def __init__(self):
        super().__init__()
        self.picker = vtk.vtkPointPicker()
        self.picker.SetTolerance(0.005)

    def get_qicon(self):
        path = ICONS_DIR / self.icon
        if path.exists():
            return QtGui.QIcon(str(path))
        return QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileIcon)

    def mouse_press(self, x: int, y: int, button: str, modifiers=None) -> bool:
        # Validação de contexto e botão
        if button != "left" or not self.context or not hasattr(self.context, 'renderer'):
            return False

        self.picker.Pick(x, y, 0, self.context.renderer)

        if self.picker.GetActor():
            pick_pos = self.picker.GetPickPosition()
            self._add_registration_point(pick_pos)
            self.render()  # Chamada delegada ao contexto para atualizar o render
            return True
        return False

    def _add_registration_point(self, position):
        # Utiliza a classe de eventos para emitir o sinal de ponto adicionado
        if self.context and hasattr(self.context, 'event_bus'):
            self.context.event_bus.emit(RegistrationEvents.POINT_ADDED, position=position)

    def on_activate(self) -> None:
        if self.context and hasattr(self.context, 'window') and self.context.window:
            self.context.window.setCursor(QtCore.Qt.CrossCursor)

    def on_deactivate(self) -> None:
        if self.context and hasattr(self.context, 'window') and self.context.window:
            self.context.window.unsetCursor()


if __name__ == "__main__":
    import sys
    from unittest.mock import MagicMock

    app = QtWidgets.QApplication(sys.argv)

    mock_context = MagicMock()
    mock_context.renderer = vtk.vtkRenderer()
    mock_context.event_bus = MagicMock()
    mock_context.window = None

    tool = AddPointRegistrationTool()
    tool.context = mock_context

    window = QtWidgets.QMainWindow()
    window.setWindowTitle(f"Teste Isolado: {tool.display_name}")

    widget_central = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(widget_central)
    btn_info = QtWidgets.QLabel("A ferramenta está ativa. Clique na cena (simulado).")
    layout.addWidget(btn_info)

    window.setCentralWidget(widget_central)
    window.resize(400, 200)
    window.show()

    print(f"Testando a ferramenta: {tool.display_name}")

    tool.mouse_press(100, 100, "left")
    sys.exit(app.exec())