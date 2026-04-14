import vtk
import os
from PySide6 import QtWidgets, QtCore, QtGui
from typing import Dict, Optional
from .planar import Janela2D
from .volume import Janela3D

class VolumeViewerWidget(QtWidgets.QWidget):
    sliceChanged = QtCore.Signal(str, int)
    PLANOS = ["Axial", "Sagital", "Coronal"]
    DIM_MAP = {"Axial": 2, "Sagital": 0, "Coronal": 1}
    NORMALS = {"Axial": (0, 0, 1), "Sagital": (1, 0, 0), "Coronal": (0, 1, 0)}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vistas: Dict[str, QtWidgets.QWidget] = {}
        self.mappers_mpr: Dict[str, vtk.vtkImageResliceMapper] = {}
        self.volume_data: Optional[vtk.vtkImageData] = None
        self.opacity_function = vtk.vtkPiecewiseFunction()

        self.path_icones = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "icones"
        )

        self.root_layout = QtWidgets.QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        self._setup_ui()

    def _setup_ui(self):
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setStyleSheet("""
            QToolBar { background: #222; border-bottom: 1px solid #333; spacing: 10px; padding: 4px; }
            QComboBox { 
                background: #333; color: white; border: 0px solid #555; 
                border-radius: 2px; padding: 1px 2px; min-width: 120px; 
            }
            QComboBox:hover { border: 1px solid #3ea6fa; }
        """)

        self.combo_layout = QtWidgets.QComboBox()
        layouts = [
            ("4 Quadrantes", "4_janelas.png"),
            ("3D Destacado", "3_1.png"),
            ("Apenas 3D", "3D.png")
        ]

        for nome, arquivo in layouts:
            icon_path = os.path.join(self.path_icones, arquivo)
            self.combo_layout.addItem(QtGui.QIcon(icon_path), nome)

        self.combo_layout.currentTextChanged.connect(self.configurar_layout)
        self.toolbar.addWidget(self.combo_layout)
        self.root_layout.addWidget(self.toolbar)

        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(2)
        self.root_layout.addWidget(self.grid_container)

        for nome in self.PLANOS:
            pane = Janela2D(nome)
            # Correção aqui: fechamento do parêntese no lambda
            pane.sliceChanged.connect(lambda v, n=nome: self.sliceChanged.emit(n, v))
            pane.windowLevelChanged.connect(self.update_window_level)
            self.vistas[nome] = pane

        pane_3d = Janela3D("3D")
        pane_3d.thresholdChanged.connect(self.update_threshold)
        self.vistas["3D"] = pane_3d

        self.configurar_layout("4 Quadrantes")

    def configurar_layout(self, modo: str):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        for p in self.vistas.values():
            p.hide()

        if modo == "4 Quadrantes":
            self.grid_layout.addWidget(self.vistas["Axial"], 0, 0)
            self.grid_layout.addWidget(self.vistas["Sagital"], 0, 1)
            self.grid_layout.addWidget(self.vistas["Coronal"], 1, 0)
            self.grid_layout.addWidget(self.vistas["3D"], 1, 1)
        elif modo == "3D Destacado":
            self.grid_layout.addWidget(self.vistas["Axial"], 0, 0)
            self.grid_layout.addWidget(self.vistas["Sagital"], 0, 1)
            self.grid_layout.addWidget(self.vistas["Coronal"], 0, 2)
            self.grid_layout.addWidget(self.vistas["3D"], 1, 0, 1, 3)
        elif modo == "Apenas 3D":
            self.grid_layout.addWidget(self.vistas["3D"], 0, 0)

        for i in range(self.grid_layout.count()):
            self.grid_layout.itemAt(i).widget().show()

    def set_volume(self, volume: vtk.vtkImageData):
        self.volume_data = volume
        extent = volume.GetExtent()

        for nome, pane in self.vistas.items():
            if pane.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer() is None:
                renderer = vtk.vtkRenderer()
                pane.vtkWidget.GetRenderWindow().AddRenderer(renderer)
            else:
                renderer = pane.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()

            if nome == "3D":
                self._configure_3d_renderer(renderer)
            else:
                self._configure_mpr_renderer(renderer, nome)
                axis = self.DIM_MAP[nome]
                total = extent[axis * 2 + 1] - extent[axis * 2] + 1
                pane.slider.blockSignals(True)
                pane.slider.setRange(0, total - 1)
                pane.slider.setValue(total // 2)
                pane.slider.blockSignals(False)

            renderer.ResetCamera()
            pane.vtkWidget.Initialize()

        self.refresh_display()

    def refresh_display(self):
        for nome, pane in self.vistas.items():
            if pane.isVisible():
                rw = pane.vtkWidget.GetRenderWindow()
                if rw:
                    # Força o VTK a ler o tamanho real do container Qt
                    rw.SetSize(pane.vtkWidget.width(), pane.vtkWidget.height())
                    # Renderiza
                    rw.Render()

    def _configure_mpr_renderer(self, renderer, plano: str):
        mapper = vtk.vtkImageResliceMapper()
        mapper.SetInputData(self.volume_data)
        mapper.SliceFacesCameraOn()
        mapper.SliceAtFocalPointOn()
        self.mappers_mpr[plano] = mapper

        plane = vtk.vtkPlane()
        plane.SetNormal(self.NORMALS[plano])
        mapper.SetSlicePlane(plane)

        actor = vtk.vtkImageSlice()
        actor.SetMapper(mapper)
        renderer.AddActor(actor)

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
        self.update_threshold(200)

    def update_threshold(self, value: int):
        self.opacity_function.RemoveAllPoints()
        self.opacity_function.AddPoint(value - 100, 0)
        self.opacity_function.AddPoint(value, 1)
        if "3D" in self.vistas:
            self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def update_slice(self, plano: str, index: int):
        if plano not in self.mappers_mpr: return
        mapper = self.mappers_mpr[plano]
        plane = mapper.GetSlicePlane()
        axis = self.DIM_MAP[plano]
        pos_fisica = self.volume_data.GetOrigin()[axis] + (index * self.volume_data.GetSpacing()[axis])

        origem = list(plane.GetOrigin())
        origem[axis] = pos_fisica
        plane.SetOrigin(origem)

        renderer = self.vistas[plano].vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        camera = renderer.GetActiveCamera()
        focal, pos = list(camera.GetFocalPoint()), list(camera.GetPosition())
        diff = pos[axis] - focal[axis]
        focal[axis], pos[axis] = pos_fisica, pos_fisica + diff
        camera.SetFocalPoint(focal)
        camera.SetPosition(pos)
        self.vistas[plano].vtkWidget.GetRenderWindow().Render()


    def update_window_level(self, window: float, level: float):
        for nome in self.PLANOS:
            if nome in self.vistas:
                renderer = self.vistas[nome].vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
                # Localiza especificamente o ator de imagem (ImageSlice)
                actor = renderer.GetActors().GetLastActor()
                if isinstance(actor, vtk.vtkImageSlice):
                    prop = actor.GetProperty()
                    prop.SetColorWindow(window)
                    prop.SetColorLevel(level)
                    self.vistas[nome].vtkWidget.GetRenderWindow().Render()

    def cleanup(self):
        for pane in self.vistas.values():
            if hasattr(pane, 'vtkWidget'):
                pane.vtkWidget.GetRenderWindow().Finalize()
                pane.vtkWidget.TerminateApp()