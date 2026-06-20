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


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    # Certifique-se de que o vtkmodules esteja instalado (pip install vtk)
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    import vtkmodules.all as vtk

    app = QApplication(sys.argv)
    window = QMainWindow()

    # 1. Widget do VTK
    frame = QWidget()
    layout = QVBoxLayout(frame)
    vtkWidget = QVTKRenderWindowInteractor(frame)
    layout.addWidget(vtkWidget)
    window.setCentralWidget(frame)

    # 2. Setup do Renderizador
    ren = vtk.vtkRenderer()
    vtkWidget.GetRenderWindow().AddRenderer(ren)

    # Adicionando um objeto (Cubo)
    cube = vtk.vtkCubeSource()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren.AddActor(actor)
    ren.ResetCamera()


    # 3. Mock do Contexto
    class MockContext:
        def __init__(self, renderer, window):
            self.renderer = renderer
            self.window = window
            self.event_bus = type('MockBus', (), {
                'emit': lambda self, name, **kwargs: print(
                    f"\n[SUCESSO] Evento '{name}' emitido com posição: {kwargs['position']}")
            })()

        def render(self):  # Método necessário pois a Tool chama self.render()
            vtkWidget.GetRenderWindow().Render()


    # 4. Inicialização da Tool
    tool = AddPointRegistrationTool()
    tool.context = MockContext(ren, window)
    tool.on_activate()  # Define o cursor


    # 5. Conectar o clique do mouse do VTK à Tool
    def handle_click(obj, event):
        # Acessa o interator através do widget diretamente
        interactor = vtkWidget.GetRenderWindow().GetInteractor()
        x, y = interactor.GetEventPosition()

        # O VTK usa o sistema de coordenadas de tela invertido (Y de baixo para cima)
        _, height = vtkWidget.GetSize()
        y = height - y

        if not tool.mouse_press(x, y, "left"):
            print("Clique fora do objeto.")


    # A correção está aqui: acessar o interator via render window
    render_window = vtkWidget.GetRenderWindow()
    interactor = render_window.GetInteractor()
    interactor.AddObserver("LeftButtonPressEvent", handle_click)

    window.show()
    vtkWidget.Initialize()

    sys.exit(app.exec())