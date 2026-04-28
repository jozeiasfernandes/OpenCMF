from PySide6 import QtWidgets, QtCore
import vtk
from modules.mod_registration.registration_toolbar import RegistrationToolbarHandler


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

        self.toolbar_handler = RegistrationToolbarHandler(self.view_a.toolbar)
        self.main_layout.addWidget(self.view_a.toolbar)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.view_a)
        self.splitter.addWidget(self.view_b)
        self.main_layout.addWidget(self.splitter)

        self.toolbar_handler.deletePointRequested.connect(self.remover_ultimo_ponto)

        QtCore.QTimer.singleShot(500, self.setup_interactors)

    def _get_safe_renderer(self, viewer):
        """Busca o renderer 3D tentando múltiplos caminhos para evitar NoneType."""
        # 1. Tenta atributos diretos
        for attr in ['renderer_3d', 'renderer', 'ren']:
            res = getattr(viewer, attr, None)
            if res: return res

        # 2. Tenta extrair da janela de renderização do widget
        try:
            w_vtk = getattr(viewer, 'vtkWidget', viewer.findChild(QtWidgets.QWidget, "vtkWidget"))
            if w_vtk:
                return w_vtk.GetRenderWindow().GetRenderers().GetFirstRenderer()
        except:
            pass
        return None

    def setup_interactors(self):
        for view_attr, picker_attr, click_handler in [
            ('view_a', 'picker_a', self._on_click_a),
            ('view_b', 'picker_b', self._on_click_b)
        ]:
            try:
                viewer = getattr(self, view_attr)
                w_vtk = getattr(viewer, 'vtkWidget', viewer.findChild(QtWidgets.QWidget, "vtkWidget"))

                if w_vtk and w_vtk.GetRenderWindow():
                    interactor = w_vtk.GetRenderWindow().GetInteractor()
                    if interactor:
                        picker = vtk.vtkPointPicker()
                        setattr(self, picker_attr, picker)
                        interactor.SetPicker(picker)
                        interactor.AddObserver("LeftButtonPressEvent", click_handler)
            except Exception as e:
                print(f"Erro ao configurar interactor {view_attr}: {e}")

    def _on_click_a(self, obj, event):
        x, y = obj.GetEventPosition()
        renderer = self._get_safe_renderer(self.view_a)
        if renderer and hasattr(self, 'picker_a'):
            self.picker_a.Pick(x, y, 0, renderer)
            pos = self.picker_a.GetPickPosition()
            if any(pos):
                self.pontos_a.append(pos)
                self._desenhar_ponto(self.view_a, pos, (1, 0, 0))
                self.pontoAdicionado.emit("A", list(pos))

    def _on_click_b(self, obj, event):
        x, y = obj.GetEventPosition()
        renderer = self._get_safe_renderer(self.view_b)
        if renderer and hasattr(self, 'picker_b'):
            self.picker_b.Pick(x, y, 0, renderer)
            pos = self.picker_b.GetPickPosition()
            if any(pos):
                self.pontos_b.append(pos)
                self._desenhar_ponto(self.view_b, pos, (0, 1, 0))
                self.pontoAdicionado.emit("B", list(pos))

    def _desenhar_ponto(self, viewer, pos, cor):
        renderer = self._get_safe_renderer(viewer)
        if not renderer: return

        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(pos)
        sphere.SetRadius(1.5)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(cor)

        renderer.AddActor(actor)

        w_vtk = getattr(viewer, 'vtkWidget', viewer.findChild(QtWidgets.QWidget, "vtkWidget"))
        if w_vtk: w_vtk.GetRenderWindow().Render()

    def adicionar_malha_vista_a(self, nome, polydata):
        self._adicionar_generic(self.view_a, nome, polydata)
        self.objetos_a[nome] = polydata

    def adicionar_malha_vista_b(self, nome, polydata):
        self._adicionar_generic(self.view_b, nome, polydata)
        self.objetos_b[nome] = polydata

    def _adicionar_generic(self, viewer, nome, polydata):
        renderer = self._get_safe_renderer(viewer)
        if not renderer: return

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Usamos PropertyKeys para persistir o nome de forma robusta no VTK
        info = vtk.vtkInformation()
        info.Set(vtk.vtkInformationStringKey.MakeKey("name", "registration"), nome)
        actor.SetPropertyKeys(info)

        renderer.AddActor(actor)
        renderer.ResetCamera()

        w_vtk = getattr(viewer, 'vtkWidget', viewer.findChild(QtWidgets.QWidget, "w_vtk"))
        if not w_vtk: w_vtk = viewer.findChild(QtWidgets.QWidget, "vtkWidget")
        if w_vtk: w_vtk.GetRenderWindow().Render()

    def remover_objeto(self, nome):
        for v in [self.view_a, self.view_b]:
            renderer = self._get_safe_renderer(v)
            if not renderer: continue

            for actor in list(renderer.GetActors()):
                info = actor.GetPropertyKeys()
                if info and info.Has(vtk.vtkInformationStringKey.MakeKey("name", "registration")):
                    if info.Get(vtk.vtkInformationStringKey.MakeKey("name", "registration")) == nome:
                        renderer.RemoveActor(actor)

            w_vtk = getattr(v, 'vtkWidget', v.findChild(QtWidgets.QWidget, "vtkWidget"))
            if w_vtk: w_vtk.GetRenderWindow().Render()

    def get_points_a(self):
        return self.pontos_a

    def get_points_b(self):
        return self.pontos_b

    def remover_ultimo_ponto(self):
        for v, lista in [(self.view_a, self.pontos_a), (self.view_b, self.pontos_b)]:
            if not lista: continue
            renderer = self._get_safe_renderer(v)
            if not renderer: continue

            actors = list(renderer.GetActors())
            for actor in reversed(actors):
                if isinstance(actor.GetMapper().GetInputAlgorithm(), vtk.vtkSphereSource):
                    renderer.RemoveActor(actor)
                    lista.pop()
                    break

            w_vtk = getattr(v, 'vtkWidget', v.findChild(QtWidgets.QWidget, "vtkWidget"))
            if w_vtk: w_vtk.GetRenderWindow().Render()

    def limpar_marcadores(self):
        self.pontos_a = []
        self.pontos_b = []
        for v in [self.view_a, self.view_b]:
            renderer = self._get_safe_renderer(v)
            if not renderer: continue
            for actor in list(renderer.GetActors()):
                if isinstance(actor.GetMapper().GetInputAlgorithm(), vtk.vtkSphereSource):
                    renderer.RemoveActor(actor)

            w_vtk = getattr(v, 'vtkWidget', v.findChild(QtWidgets.QWidget, "vtkWidget"))
            if w_vtk: w_vtk.GetRenderWindow().Render()