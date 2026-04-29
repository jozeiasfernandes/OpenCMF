import vtk
import os
import json
from PySide6 import QtWidgets, QtCore
from typing import Dict, Optional

from core.components.windows.window_2d.window_2d import Janela2D
from core.components.windows.window_3d.window_3d import Janela3D
from core.volume.lookup_table.lut_manager import LUTManager
from .viewer_utils.viewer_renderers import ViewerRenderers


class VolumeViewerWidget(QtWidgets.QWidget):
    sliceChanged = QtCore.Signal(str, int)
    windowLevelChanged = QtCore.Signal(float, float)

    PLANOS = ["Axial", "Sagital", "Coronal"]
    DIM_MAP = {"Axial": 2, "Sagital": 0, "Coronal": 1}
    NORMALS = {"Axial": (0, 0, 1), "Sagital": (1, 0, 0), "Coronal": (0, 1, 0)}
    VIEW_UP = {"Axial": (0, -1, 0), "Sagital": (0, 0, 1), "Coronal": (0, 0, 1)}

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
        self.path_presets = os.path.abspath(os.path.join(base_path, "..", "presets"))
        self.path_icones = os.path.abspath(os.path.join(base_path, "..", "..", "icons"))

    def _setup_main_layout(self):
        self.root_layout = QtWidgets.QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # Toolbar interna removida para evitar duplicidade com a toolbar do Modulo

        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(2)
        self.root_layout.addWidget(self.grid_container)

        self._create_viewers()
        self.configurar_layout("4 Quadrantes")

    def _create_viewers(self):
        cores = {"Axial": "#D32F2F", "Sagital": "#FBC02D", "Coronal": "#388E3C"}
        for nome in self.PLANOS:
            pane = Janela2D(nome, cores[nome])
            pane.sliceChanged.connect(lambda v, n=nome: self.update_slice(n, v))
            pane.maximizeRequested.connect(lambda maximo, n=nome: self._handle_maximize(n, maximo))
            pane.lutChanged.connect(self.apply_global_lut)
            self.vistas[nome] = pane

        pane_3d = Janela3D("3D", "#1976D2")
        pane_3d.thresholdChanged.connect(self.update_threshold)
        pane_3d.viewChanged.connect(self.update_3d_view)
        pane_3d.presetChanged.connect(self.update_preset)
        pane_3d.maximizeRequested.connect(lambda maximo: self._handle_maximize("3D", maximo))
        self.vistas["3D"] = pane_3d

    def apply_global_lut(self, lut_name: str):
        new_lut = LUTManager.get_vtk_lut(lut_name)

        for nome in self.PLANOS:
            pane = self.vistas.get(nome)
            if pane and hasattr(pane, 'vtk_property') and pane.vtk_property:
                pane.vtk_property.SetLookupTable(new_lut)
                pane.vtkWidget.GetRenderWindow().Render()

    def set_volume(self, volume: vtk.vtkImageData):
        self.volume_data = volume
        extent = volume.GetExtent()
        centro = volume.GetCenter()

        for nome, pane in self.vistas.items():
            rw = pane.vtkWidget.GetRenderWindow()
            ren = rw.GetRenderers().GetFirstRenderer()
            if not ren:
                ren = vtk.vtkRenderer()
                rw.AddRenderer(ren)

            if nome == "3D":
                self.volume_actor = ViewerRenderers.configure_3d_renderer(
                    ren, volume, self.color_function, self.opacity_function
                )
                initial_preset = self.vistas["3D"].combo_presets.currentText()
                if initial_preset:
                    QtCore.QTimer.singleShot(50, lambda: self.update_preset(initial_preset))
            else:
                axis = self.DIM_MAP[nome]
                actor_2d = ViewerRenderers.configure_mpr_renderer(
                    ren, volume, self.NORMALS[nome], centro
                )

                self.mappers_mpr[nome] = actor_2d.GetMapper()
                pane.vtk_property = actor_2d.GetProperty()

                min_s, max_s = extent[axis * 2], extent[axis * 2 + 1]
                pane.slider_corte.setRange(min_s, max_s)
                slice_init = (min_s + max_s) // 2
                pane.slider_corte.setValue(slice_init)

                ViewerRenderers.setup_camera_mpr(
                    ren, centro, axis, self.VIEW_UP[nome], nome == "Axial"
                )
                self.update_slice(nome, slice_init)

            rw.Render()

    def update_slice(self, plano: str, index: int):
        if not self.volume_data or plano not in self.mappers_mpr: return

        axis = self.DIM_MAP[plano]
        spacing = self.volume_data.GetSpacing()[axis]
        origin = self.volume_data.GetOrigin()[axis]
        pos_fisica = origin + (index * spacing)

        ViewerRenderers.update_reslice_position(self.mappers_mpr[plano], axis, pos_fisica)

        pane = self.vistas[plano]
        renderer = pane.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        cam = renderer.GetActiveCamera()

        focal = list(cam.GetFocalPoint())
        pos = list(cam.GetPosition())
        dist = pos[axis] - focal[axis]
        focal[axis] = pos_fisica
        pos[axis] = pos_fisica + dist

        cam.SetFocalPoint(focal)
        cam.SetPosition(pos)
        pane.lbl_mm.setText(f"{pos_fisica:.1f} mm")
        pane.vtkWidget.GetRenderWindow().Render()
        self.sliceChanged.emit(plano, index)

    def update_preset(self, nome: str):
        if not self.volume_actor: return
        path = os.path.join(self.path_presets, f"{nome}.json")
        if not os.path.exists(path): return

        with open(path, "r") as f:
            preset = json.load(f)

        self.color_function.RemoveAllPoints()
        self.opacity_function.RemoveAllPoints()
        for p in preset.get("colors", []): self.color_function.AddRGBPoint(*p)
        for p in preset.get("opacity", []): self.opacity_function.AddPoint(*p)

        threshold = preset.get("threshold", 400)
        self.vistas["3D"].slider_threshold.setValue(threshold)
        self.volume_actor.GetProperty().SetShade(preset.get("shade", True))

        if preset.get("mip"):
            self.volume_actor.GetMapper().SetBlendModeToMaximumIntensity()
        else:
            self.volume_actor.GetMapper().SetBlendModeToComposite()

        self.update_threshold(threshold)
        self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def update_threshold(self, value: int):
        if not self.volume_actor: return
        self.opacity_function.RemoveAllPoints()
        self.opacity_function.AddPoint(value - 100, 0.0)
        self.opacity_function.AddPoint(value, 0.2)
        self.opacity_function.AddPoint(value + 500, 0.8)
        self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def update_3d_view(self, vista: str):
        ren = self.vistas["3D"].vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        maps = {
            "Frente": (0, -1, 0, 0, 0, 1), "Posterior": (0, 1, 0, 0, 0, 1),
            "Superior": (0, 0, 1, 0, -1, 0), "Inferior": (0, 0, -1, 0, 1, 0),
            "Direito": (1, 0, 0, 0, 0, 1), "Esquerdo": (-1, 0, 0, 0, 0, 1)
        }
        if vista in maps:
            cam = ren.GetActiveCamera()
            cam.SetPosition(maps[vista][:3])
            cam.SetViewUp(maps[vista][3:])
            cam.SetFocalPoint(0, 0, 0)
            ren.ResetCamera()
            self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def configurar_layout(self, modo: str):
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w: w.setParent(None)

        for n, obj in self.vistas.items():
            obj.hide()
            if hasattr(obj, 'is_maximized'):
                obj.is_maximized = (modo == n or (modo == "Apenas 3D" and n == "3D"))
                obj._update_maximize_icon()

        mapping = {
            "4 Quadrantes": [("Axial", 0, 0), ("Sagital", 0, 1), ("Coronal", 1, 0), ("3D", 1, 1)],
            "3D Destacado": [("Axial", 0, 0), ("Sagital", 0, 1), ("Coronal", 0, 2), ("3D", 1, 0, 1, 3)],
            "Apenas 3D": [("3D", 0, 0)], "Axial": [("Axial", 0, 0)],
            "Sagital": [("Sagital", 0, 0)], "Coronal": [("Coronal", 0, 0)]
        }
        for item in mapping.get(modo, []):
            self.grid_layout.addWidget(self.vistas[item[0]], *item[1:])
            self.vistas[item[0]].show()

    def refresh_display(self):
        for p in self.vistas.values():
            if p.isVisible(): p.vtkWidget.GetRenderWindow().Render()

    def _handle_maximize(self, nome, is_max):
        if is_max:
            modo = "Apenas 3D" if nome == "3D" else nome
            self.configurar_layout(modo)
        else:
            self.configurar_layout("4 Quadrantes")