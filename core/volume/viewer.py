import vtk
import os
from PySide6 import QtWidgets, QtCore, QtGui
from typing import Dict, Optional
from core.windows.janela2d import Janela2D
from core.windows.janela3d import Janela3D


class VolumeViewerWidget(QtWidgets.QWidget):
    sliceChanged = QtCore.Signal(str, int)
    windowLevelChanged = QtCore.Signal(float, float)

    PLANOS = ["Axial", "Sagital", "Coronal"]
    DIM_MAP = {"Axial": 2, "Sagital": 0, "Coronal": 1}
    NORMALS = {"Axial": (0, 0, 1), "Sagital": (1, 0, 0), "Coronal": (0, 1, 0)}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vistas: Dict[str, QtWidgets.QWidget] = {}
        self.mappers_mpr: Dict[str, vtk.vtkImageResliceMapper] = {}
        self.volume_data: Optional[vtk.vtkImageData] = None
        self.opacity_function = vtk.vtkPiecewiseFunction()
        self.color_function = vtk.vtkColorTransferFunction()
        self.volume_actor: Optional[vtk.vtkVolume] = None

        self._init_paths()
        self._setup_main_layout()

    def _init_paths(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.path_icones = os.path.abspath(os.path.join(base_path, "../..", "..", "icons"))

    def _setup_main_layout(self):
        self.root_layout = QtWidgets.QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self._setup_toolbar()

        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(4)
        self.root_layout.addWidget(self.grid_container)

        self._create_viewers()
        self.configurar_layout("4 Quadrantes")

    def _setup_toolbar(self):
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setFixedHeight(38)
        self.toolbar.setStyleSheet("""
            QToolBar { background: #1E1E1E; border-bottom: 1px solid #333; spacing: 8px; }
            QComboBox { background: #333; color: white; border: 1px solid #444; padding: 2px 10px; }
        """)

        self.combo_layout = QtWidgets.QComboBox()
        layouts = [("4 Quadrantes", "4_janelas.png"), ("3D Destacado", "3_1.png"), ("Apenas 3D", "3D.png")]

        for nome, img in layouts:
            icon_path = os.path.join(self.path_icones, img)
            self.combo_layout.addItem(QtGui.QIcon(icon_path), nome)

        self.combo_layout.currentTextChanged.connect(self.configurar_layout)
        self.toolbar.addWidget(QtWidgets.QLabel("  Layout: "))
        self.toolbar.addWidget(self.combo_layout)
        self.root_layout.addWidget(self.toolbar)

    def _create_viewers(self):
        cores = {"Axial": "#D32F2F", "Sagital": "#FBC02D", "Coronal": "#388E3C"}

        for nome in self.PLANOS:
            pane = Janela2D(nome, cores[nome])
            pane.sliceChanged.connect(lambda v, n=nome: self.update_slice(n, v))
            self.vistas[nome] = pane

        pane_3d = Janela3D("3D", "#1976D2")
        pane_3d.thresholdChanged.connect(self.update_threshold)
        pane_3d.viewChanged.connect(self.update_3d_view)
        self.vistas["3D"] = pane_3d

    def set_volume(self, volume: vtk.vtkImageData):
        self.volume_data = volume
        extent = volume.GetExtent()

        for nome, pane in self.vistas.items():
            rw = pane.vtkWidget.GetRenderWindow()
            ren = rw.GetRenderers().GetFirstRenderer() or vtk.vtkRenderer()
            if not rw.GetRenderers().GetFirstRenderer(): rw.AddRenderer(ren)

            if nome == "3D":
                self._configure_3d_renderer(ren)
            else:
                self._configure_mpr_renderer(ren, nome)
                axis = self.DIM_MAP[nome]
                max_slice = extent[axis * 2 + 1] - extent[axis * 2]

                pane.slider_corte.blockSignals(True)
                pane.slider_corte.setRange(0, max_slice)
                pane.slider_corte.setValue(max_slice // 2)
                pane.slider_corte.blockSignals(False)
                self.update_slice(nome, max_slice // 2)

            ren.ResetCamera()
            rw.Render()

    def _configure_mpr_renderer(self, renderer, plano: str):
        renderer.RemoveAllViewProps()
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
        actor.GetProperty().SetColorWindow(2000)
        actor.GetProperty().SetColorLevel(500)
        actor.GetProperty().SetInterpolationTypeToLinear()
        renderer.AddActor(actor)

    def _configure_3d_renderer(self, renderer):
        renderer.RemoveAllViewProps()
        mapper = vtk.vtkSmartVolumeMapper()
        mapper.SetInputData(self.volume_data)
        mapper.SetRequestedRenderModeToRayCast()

        self.color_function.AddRGBPoint(-1000, 0.0, 0.0, 0.0)
        self.color_function.AddRGBPoint(400, 0.8, 0.6, 0.5)
        self.color_function.AddRGBPoint(2000, 1.0, 1.0, 0.9)

        prop = vtk.vtkVolumeProperty()
        prop.ShadeOn()
        prop.SetColor(self.color_function)
        prop.SetScalarOpacity(self.opacity_function)
        prop.SetInterpolationTypeToLinear()

        self.volume_actor = vtk.vtkVolume()
        self.volume_actor.SetMapper(mapper)
        self.volume_actor.SetProperty(prop)
        renderer.AddActor(self.volume_actor)
        self.update_threshold(400)

    def update_slice(self, plano: str, index: int):
        if not self.volume_data or plano not in self.mappers_mpr: return
        axis = self.DIM_MAP[plano]
        pos = self.volume_data.GetOrigin()[axis] + (index * self.volume_data.GetSpacing()[axis])

        plane = self.mappers_mpr[plano].GetSlicePlane()
        origin = list(plane.GetOrigin())
        origin[axis] = pos
        plane.SetOrigin(origin)

        self.vistas[plano].lbl_mm.setText(f"{pos:.1f} mm")
        self.vistas[plano].vtkWidget.GetRenderWindow().Render()

    def update_threshold(self, value: int):
        if not self.volume_actor: return
        self.opacity_function.RemoveAllPoints()
        self.opacity_function.AddPoint(value - 100, 0.0)
        self.opacity_function.AddPoint(value, 0.2)
        self.opacity_function.AddPoint(value + 500, 0.8)
        self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def update_3d_view(self, vista: str):
        if "3D" not in self.vistas: return
        renderer = self.vistas["3D"].vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        cam = renderer.GetActiveCamera()

        maps = {
            "Frente":    (0, -1, 0,  0, 0, 1),
            "Posterior": (0, 1, 0,   0, 0, 1),
            "Superior":  (0, 0, 1,   0, -1, 0),
            "Inferior":  (0, 0, -1,  0, 1, 0),
            "Direito":   (1, 0, 0,   0, 0, 1),
            "Esquerdo":  (-1, 0, 0,  0, 0, 1)
        }

        if vista in maps:
            pos, up = maps[vista][:3], maps[vista][3:]
            cam.SetPosition(pos)
            cam.SetViewUp(up)
            cam.SetFocalPoint(0, 0, 0)
            renderer.ResetCamera()
            self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def configurar_layout(self, modo: str):
        for i in reversed(range(self.grid_layout.count())):
            if self.grid_layout.itemAt(i).widget():
                self.grid_layout.itemAt(i).widget().setParent(None)

        for v in self.vistas.values(): v.hide()

        mapping = {
            "4 Quadrantes": [("Axial", 0, 0), ("Sagital", 0, 1), ("Coronal", 1, 0), ("3D", 1, 1)],
            "3D Destacado": [("Axial", 0, 0), ("Sagital", 0, 1), ("Coronal", 0, 2), ("3D", 1, 0, 1, 3)],
            "Apenas 3D": [("3D", 0, 0)]
        }

        for item in mapping.get(modo, []):
            self.grid_layout.addWidget(self.vistas[item[0]], *item[1:])
            self.vistas[item[0]].show()

    def refresh_display(self):
        for pane in self.vistas.values():
            if pane.isVisible():
                pane.vtkWidget.GetRenderWindow().Render()