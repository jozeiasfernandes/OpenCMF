from PySide6 import QtWidgets, QtCore
import vtk


class WindowRegistration(QtWidgets.QWidget):
    pontoAdicionado = QtCore.Signal(str, list)

    def __init__(self):
        super().__init__()
        self.objetos_a = {}
        self.objetos_b = {}
        self.pontos_a = []
        self.pontos_b = []
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        from core.volume.viewer import VolumeViewerWidget
        self.view_a = VolumeViewerWidget()
        self.view_a.configurar_layout("Apenas 3D")

        self.view_b = VolumeViewerWidget()
        self.view_b.configurar_layout("Apenas 3D")
        self.view_b.toolbar.hide()

        # Usamos a toolbar da view_a como toolbar única do módulo
        self.main_layout.addWidget(self.view_a.toolbar)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.view_a)
        self.splitter.addWidget(self.view_b)

        self.main_layout.addWidget(self.splitter)

        QtCore.QTimer.singleShot(100, self.setup_interactors)

    def setup_interactors(self):
        try:
            w_a = getattr(self.view_a, 'vtkWidget', self.view_a.findChild(QtWidgets.QWidget, "vtkWidget"))
            w_b = getattr(self.view_b, 'vtkWidget', self.view_b.findChild(QtWidgets.QWidget, "vtkWidget"))

            self.picker_a = vtk.vtkPointPicker()
            w_a.GetInteractor().SetPicker(self.picker_a)
            w_a.GetInteractor().AddObserver("LeftButtonPressEvent", self._on_click_a)

            self.picker_b = vtk.vtkPointPicker()
            w_b.GetInteractor().SetPicker(self.picker_b)
            w_b.GetInteractor().AddObserver("LeftButtonPressEvent", self._on_click_b)
        except Exception as e:
            print(f"Erro interactors: {e}")

    def _on_click_a(self, obj, event):
        x, y = obj.GetEventPosition()
        self.picker_a.Pick(x, y, 0, self.view_a.renderer_3d)
        pos = self.picker_a.GetPickPosition()
        if any(pos):
            self.pontos_a.append(pos)
            self._desenhar_ponto(self.view_a, pos, (1, 0, 0))
            self.pontoAdicionado.emit("A", list(pos))

    def _on_click_b(self, obj, event):
        x, y = obj.GetEventPosition()
        self.picker_b.Pick(x, y, 0, self.view_b.renderer_3d)
        pos = self.picker_b.GetPickPosition()
        if any(pos):
            self.pontos_b.append(pos)
            self._desenhar_ponto(self.view_b, pos, (0, 1, 0))
            self.pontoAdicionado.emit("B", list(pos))

    def _desenhar_ponto(self, viewer, pos, cor):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(pos)
        sphere.SetRadius(1.5)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(cor)
        viewer.renderer_3d.AddActor(actor)

        w = getattr(viewer, 'vtkWidget', viewer.findChild(QtWidgets.QWidget, "vtkWidget"))
        w.GetRenderWindow().Render()

    def adicionar_malha_vista_a(self, nome, polydata):
        self.view_a.adicionar_malha_3d(nome, polydata)
        self.objetos_a[nome] = polydata

    def adicionar_malha_vista_b(self, nome, polydata):
        self.view_b.adicionar_malha_3d(nome, polydata)
        self.objetos_b[nome] = polydata

    def remover_objeto(self, nome):
        self.view_a.remover_objeto(nome)
        self.view_b.remover_objeto(nome)

    def get_points_a(self):
        return self.pontos_a

    def get_points_b(self):
        return self.pontos_b

    def limpar_marcadores(self):
        self.pontos_a = []
        self.pontos_b = []
        for v in [self.view_a, self.view_b]:
            for actor in list(v.renderer_3d.GetActors()):
                if isinstance(actor.GetMapper().GetInputAlgorithm(), vtk.vtkSphereSource):
                    v.renderer_3d.RemoveActor(actor)
            w = getattr(v, 'vtkWidget', v.findChild(QtWidgets.QWidget, "vtkWidget"))
            w.GetRenderWindow().Render()