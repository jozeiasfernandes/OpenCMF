import vtk
from PySide6 import QtWidgets, QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from typing import Dict, Optional


class PlanarViewer(QtWidgets.QWidget):
    sliceChanged = QtCore.Signal(int)

    def __init__(self, nome: str, parent=None):
        super().__init__(parent)
        self.nome = nome
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vtkWidget.setStyleSheet("background-color: black; border: 1px solid #222;")

        self.indicator = QtWidgets.QLabel(nome, self.vtkWidget)
        self.indicator.setStyleSheet("color: #3ea6fa; background: rgba(0,0,0,150); font-weight: bold; padding: 2px;")
        self.indicator.move(5, 5)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setStyleSheet("height: 20px;")  # Aumentado para garantir visibilidade/clique
        self.slider.hide()

        self.layout.addWidget(self.vtkWidget, stretch=1)
        self.layout.addWidget(self.slider)

        # Conexão direta e imediata
        self.slider.valueChanged.connect(self.sliceChanged.emit)


class VolumeViewerWidget(QtWidgets.QWidget):
    sliceChanged = QtCore.Signal(str, int)

    PLANOS = ["Axial", "Sagital", "Coronal"]
    DIM_MAP = {"Axial": 2, "Sagital": 0, "Coronal": 1}
    NORMALS = {"Axial": (0, 0, 1), "Sagital": (1, 0, 0), "Coronal": (0, 1, 0)}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vistas: Dict[str, PlanarViewer] = {}
        self.mappers_mpr: Dict[str, vtk.vtkImageResliceMapper] = {}
        self.volume_data: Optional[vtk.vtkImageData] = None
        self.opacity_function = vtk.vtkPiecewiseFunction()
        self._initialize_ui()

    def _initialize_ui(self):
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        for i, nome in enumerate(self.PLANOS + ["3D"]):
            pane = PlanarViewer(nome)
            if nome != "3D":
                # Uso de functools ou default argument para evitar problemas de closure do lambda
                pane.sliceChanged.connect(lambda v, n=nome: self.sliceChanged.emit(n, v))
                pane.vtkWidget.AddObserver("MouseWheelForwardEvent", self._handle_scroll)
                pane.vtkWidget.AddObserver("MouseWheelBackwardEvent", self._handle_scroll)

            self.vistas[nome] = pane
            layout.addWidget(pane, i // 2, i % 2)

    def set_volume(self, volume: vtk.vtkImageData):
        self.volume_data = volume
        extent = volume.GetExtent()

        for nome, pane in self.vistas.items():
            if nome == "3D":
                renderer = vtk.vtkRenderer()
                pane.vtkWidget.GetRenderWindow().AddRenderer(renderer)
                self._configure_3d_renderer(renderer)
            else:
                renderer = vtk.vtkRenderer()
                pane.vtkWidget.GetRenderWindow().AddRenderer(renderer)
                self._configure_mpr_renderer(renderer, nome)

                axis = self.DIM_MAP[nome]
                total = extent[axis * 2 + 1] - extent[axis * 2] + 1

                pane.slider.blockSignals(True)
                pane.slider.setRange(0, total - 1)
                pane.slider.setValue(total // 2)
                pane.slider.blockSignals(False)
                pane.slider.show()

            renderer.ResetCamera()
            pane.vtkWidget.Initialize()

        self.refresh_display()

    def _configure_mpr_renderer(self, renderer, plano: str):
        mapper = vtk.vtkImageResliceMapper()
        mapper.SetInputData(self.volume_data)
        mapper.SliceFacesCameraOn()
        mapper.SliceAtFocalPointOn()
        mapper.SetResampleToScreenPixels(True)
        self.mappers_mpr[plano] = mapper

        plane = vtk.vtkPlane()
        plane.SetNormal(self.NORMALS[plano])
        mapper.SetSlicePlane(plane)

        actor = vtk.vtkImageSlice()
        actor.SetMapper(mapper)
        renderer.AddActor(actor)
        renderer.SetBackground(0.05, 0.05, 0.05)

        # Setup inicial da câmera
        bounds = self.volume_data.GetBounds()
        center = [(bounds[i * 2] + bounds[i * 2 + 1]) / 2.0 for i in range(3)]
        camera = renderer.GetActiveCamera()
        camera.ParallelProjectionOn()
        camera.SetFocalPoint(center)
        pos = list(center)
        pos[self.DIM_MAP[plano]] += 1000 if plano != "Coronal" else -1000
        camera.SetPosition(pos)

        ups = {"Axial": (0, -1, 0), "Sagital": (0, 0, 1), "Coronal": (0, 0, 1)}
        camera.SetViewUp(ups[plano])

    def update_slice(self, plano: str, index: int):
        if plano not in self.mappers_mpr or not self.volume_data:
            return

        mapper = self.mappers_mpr[plano]
        plane = mapper.GetSlicePlane()
        axis = self.DIM_MAP[plano]

        pos_fisica = self.volume_data.GetOrigin()[axis] + (index * self.volume_data.GetSpacing()[axis])

        # Move Plano
        origem = list(plane.GetOrigin())
        origem[axis] = pos_fisica
        plane.SetOrigin(origem)

        # Sincroniza Câmera
        renderer = self.vistas[plano].vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        camera = renderer.GetActiveCamera()
        focal = list(camera.GetFocalPoint())
        pos = list(camera.GetPosition())
        diff = pos[axis] - focal[axis]
        focal[axis] = pos_fisica
        pos[axis] = pos_fisica + diff
        camera.SetFocalPoint(focal)
        camera.SetPosition(pos)

        self.vistas[plano].vtkWidget.GetRenderWindow().Render()

    def _handle_scroll(self, interactor, event):
        step = 1 if event == "MouseWheelForwardEvent" else -1
        plano = next((n for n, p in self.vistas.items() if p.vtkWidget == interactor), None)
        if plano:
            slider = self.vistas[plano].slider
            slider.setValue(slider.value() + step)

    def _configure_3d_renderer(self, renderer):
        mapper = vtk.vtkGPUVolumeRayCastMapper()
        mapper.SetInputData(self.volume_data)
        prop = vtk.vtkVolumeProperty()
        prop.ShadeOn()
        prop.SetInterpolationTypeToLinear()
        prop.SetScalarOpacity(self.opacity_function)
        vol = vtk.vtkVolume()
        vol.SetMapper(mapper)
        vol.SetProperty(prop)
        renderer.AddActor(vol)
        renderer.SetBackground(0.1, 0.1, 0.15)
        self.update_threshold(200, False)

    def update_threshold(self, value: int, render=True):
        self.opacity_function.RemoveAllPoints()
        self.opacity_function.AddPoint(value - 100, 0)
        self.opacity_function.AddPoint(value, 1)
        if render and "3D" in self.vistas:
            self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def refresh_display(self):
        for pane in self.vistas.values():
            if pane.vtkWidget.GetRenderWindow():
                pane.vtkWidget.GetRenderWindow().Render()

    def cleanup(self):
        for pane in self.vistas.values():
            pane.vtkWidget.GetRenderWindow().Finalize()
            pane.vtkWidget.TerminateApp()