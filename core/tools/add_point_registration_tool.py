import vtk
from PySide6 import QtWidgets, QtCore, QtGui
from core.tools.base.base_tool import BaseTool
from core.localization.translator import get_base_dir

class AddPointRegistrationTool(BaseTool):
    name = "add_point"
    display_name = "Adicionar Pontos"
    icon = "add_point.svg"
    tool_tip = "Clique na superfície do objeto para adicionar um ponto de registro."

    def __init__(self):
        super().__init__()
        self.picker = vtk.vtkPointPicker()
        self.picker.SetTolerance(0.005)

    def get_qicon(self):
        path = get_base_dir() / "appearance" / "icons" / self.icon
        if path.exists():
            return QtGui.QIcon(str(path))
        return QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileIcon)

    def mouse_press(self, x: int, y: int, button: str, modifiers=None) -> bool:
        if button != "left" or not self.context:
            return False
        self.picker.Pick(x, y, 0, self.context.renderer)
        pick_pos = self.picker.GetPickPosition()
        if self.picker.GetActor():
            self._add_registration_point(pick_pos)
            self.render()
            return True
        return False

    def _add_registration_point(self, position):
        if self.context and hasattr(self.context, 'event_bus'):
            self.context.event_bus.emit("REGISTRATION_POINT_ADDED", position=position)

    def on_activate(self) -> None:
        if self.context and self.context.window:
            self.context.window.setCursor(QtCore.Qt.CrossCursor)

    def on_deactivate(self) -> None:
        if self.context and self.context.window:
            self.context.window.unsetCursor()