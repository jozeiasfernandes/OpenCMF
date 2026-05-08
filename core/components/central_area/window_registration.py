from PySide6 import QtWidgets, QtCore
import vtk
import sys
from core.components.central_area.windows_3d import Janela3DSurface


class RegistrationDoubleClickFilter(QtCore.QObject):
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            return True
        return super().eventFilter(obj, event)


class WindowRegistration(QtWidgets.QWidget):
    pontoAdicionado = QtCore.Signal(str, list)

    def __init__(self):
        super().__init__()
        self.objetos_a = {}
        self.objetos_b = {}
        self.pontos_a = []
        self.pontos_b = []
        self.current_point_size = 1.5
        self.db_click_filter = RegistrationDoubleClickFilter(self)
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.view_a = Janela3DSurface("Vista A", "#00AAFF")
        self.view_b = Janela3DSurface("Vista B", "#555555")

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.view_a)
        self.splitter.addWidget(self.view_b)
        self.main_layout.addWidget(self.splitter)

        QtCore.QTimer.singleShot(100, self._finalize_setup)

    def set_objeto_opacidade(self, nome: str, valor: float):
        for view in [self.view_a, self.view_b]:
            if nome in view.atores_malha:
                view.atores_malha[nome].GetProperty().SetOpacity(valor)
                view.render()

    def set_objeto_cor(self, nome: str, rgb: tuple):
        for view in [self.view_a, self.view_b]:
            if nome in view.atores_malha:
                view.atores_malha[nome].GetProperty().SetColor(rgb)
                view.render()

    def set_ponto_raio(self, size: float):
        self.current_point_size = size
        for view in [self.view_a, self.view_b]:
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            for _ in range(actors.GetNumberOfItems()):
                actor = actors.GetNextActor()
                mapper = actor.GetMapper()
                if mapper:
                    algo = mapper.GetInputAlgorithm()
                    if isinstance(algo, vtk.vtkSphereSource):
                        algo.SetRadius(size)
            view.render()

    def _finalize_setup(self):
        self.reset_layout_vistas()
        self.setup_interactors()

    def reset_layout_vistas(self):
        total_width = self.splitter.width()
        self.splitter.setSizes([total_width // 2, total_width // 2])
        self.view_a.reset_camera()
        self.view_b.reset_camera()

    def setup_interactors(self):
        self.view_a.setup_interactors()
        self.view_b.setup_interactors()

        for view, picker_attr, click_handler in [
            (self.view_a, 'picker_a', self._on_click_a),
            (self.view_b, 'picker_b', self._on_click_b)
        ]:
            interactor = view.vtkWidget.GetRenderWindow().GetInteractor()
            picker = vtk.vtkPointPicker()
            setattr(self, picker_attr, picker)
            interactor.SetPicker(picker)
            interactor.AddObserver("LeftButtonPressEvent", click_handler)

    def _on_click_a(self, obj, event):
        x, y = obj.GetEventPosition()
        self.picker_a.Pick(x, y, 0, self.view_a.renderer)
        pos = self.picker_a.GetPickPosition()
        if any(pos):
            self.pontos_a.append(pos)
            self._desenhar_ponto(self.view_a, pos, (1, 0, 0))
            self.pontoAdicionado.emit("A", list(pos))

    def _on_click_b(self, obj, event):
        x, y = obj.GetEventPosition()
        self.picker_b.Pick(x, y, 0, self.view_b.renderer)
        pos = self.picker_b.GetPickPosition()
        if any(pos):
            self.pontos_b.append(pos)
            self._desenhar_ponto(self.view_b, pos, (0, 1, 0))
            self.pontoAdicionado.emit("B", list(pos))

    def _desenhar_ponto(self, view, pos, cor):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(pos)
        sphere.SetRadius(self.current_point_size)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(cor)
        view.renderer.AddActor(actor)
        view.render()

    def adicionar_malha_vista_a(self, nome, polydata):
        self.view_a.adicionar_objeto(nome, polydata, cor=(0.7, 0.7, 0.9))
        self.objetos_a[nome] = polydata

    def adicionar_malha_vista_b(self, nome, polydata):
        self.view_b.adicionar_objeto(nome, polydata, cor=(0.9, 0.9, 0.7))
        self.objetos_b[nome] = polydata

    def remover_objeto(self, nome):
        self.view_a.remover_objeto(nome)
        self.view_b.remover_objeto(nome)

    def get_points_a(self):
        return self.pontos_a

    def get_points_b(self):
        return self.pontos_b

    def remover_ultimo_marcador(self):
        for view, lista in [(self.view_a, self.pontos_a), (self.view_b, self.pontos_b)]:
            if not lista: continue
            actors = list(view.renderer.GetActors())
            for actor in reversed(actors):
                mapper = actor.GetMapper()
                if mapper:
                    algo = mapper.GetInputAlgorithm()
                    if isinstance(algo, vtk.vtkSphereSource):
                        view.renderer.RemoveActor(actor)
                        lista.pop()
                        break
            view.render()

    def limpar_marcadores(self):
        self.pontos_a = []
        self.pontos_b = []
        for view in [self.view_a, self.view_b]:
            actors = list(view.renderer.GetActors())
            for actor in actors:
                mapper = actor.GetMapper()
                if mapper:
                    algo = mapper.GetInputAlgorithm()
                    if isinstance(algo, vtk.vtkSphereSource):
                        view.renderer.RemoveActor(actor)
            view.render()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.resize(1024, 768)
    registration_widget = WindowRegistration()
    window.setCentralWidget(registration_widget)
    window.show()
    sys.exit(app.exec())