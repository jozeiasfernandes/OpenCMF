import os
import json
import vtk
from typing import Dict, Any, Callable, Optional
from domain.volume.visualization.lut.lut_manager import LUTManager
from domain.volume.visualization.volume_viewer.viewer_utils.viewer_renderers import ViewerRenderers
from domain.volume.visualization.volume_viewer.constants import VolumeViewerConstants


class VolumeViewerController:
    def __init__(self, vistas: Dict[str, Any], path_presets: str):
        self.vistas = vistas
        self.path_presets = path_presets

        self.volume_data: Optional[vtk.vtkImageData] = None
        self.volume_actor: Optional[vtk.vtkVolume] = None
        self.mappers_mpr: Dict[str, vtk.vtkImageResliceMapper] = {}

        self.opacity_function = vtk.vtkPiecewiseFunction()
        self.color_function = vtk.vtkColorTransferFunction()

    def render_volume(self, volume: vtk.vtkImageData):
        self.volume_data = volume
        ext, centro = volume.GetExtent(), volume.GetCenter()

        for nome, pane in self.vistas.items():
            rw = pane.vtkWidget.GetRenderWindow()
            ren = rw.GetRenderers().GetFirstRenderer() or vtk.vtkRenderer()
            if not rw.GetRenderers().GetFirstRenderer():
                rw.AddRenderer(ren)

            if nome == "3D":
                self.volume_actor = ViewerRenderers.configure_3d_renderer(
                    ren, volume, self.color_function, self.opacity_function
                )
                preset = getattr(pane, 'combo_presets', None)
                preset_name = preset.currentText() if preset else ""
                if preset_name:
                    # Pode ser acionado externamente se necessário
                    pass
            else:
                axis = VolumeViewerConstants.DIM_MAP[nome]
                actor = ViewerRenderers.configure_mpr_renderer(
                    ren, volume, VolumeViewerConstants.NORMALS[nome], centro
                )

                self.mappers_mpr[nome] = actor.GetMapper()
                pane.vtk_property = actor.GetProperty()

                min_s, max_s = ext[axis * 2], ext[axis * 2 + 1]
                if hasattr(pane, 'slider_corte'):
                    pane.slider_corte.setRange(min_s, max_s)

                ViewerRenderers.setup_camera_mpr(
                    ren, centro, axis, VolumeViewerConstants.VIEW_UP[nome], nome == "Axial"
                )
                self.update_slice(nome, (min_s + max_s) // 2)

            rw.Render()

    def apply_global_lut(self, lut_name: str, toolbar=None):
        new_lut = LUTManager.get_vtk_lut(lut_name)
        if toolbar and hasattr(toolbar, 'set_lut_text'):
            toolbar.set_lut_text(lut_name)

        for nome in VolumeViewerConstants.PLANES:
            pane = self.vistas.get(nome)
            if pane and hasattr(pane, 'vtk_property') and pane.vtk_property:
                pane.vtk_property.SetLookupTable(new_lut)
                pane.vtkWidget.GetRenderWindow().Render()

    def update_slice(self, plano: str, index: int) -> Optional[float]:
        if not self.volume_data or plano not in self.mappers_mpr:
            return None

        axis = VolumeViewerConstants.DIM_MAP[plano]
        pos_fisica = self.volume_data.GetOrigin()[axis] + (index * self.volume_data.GetSpacing()[axis])

        ViewerRenderers.update_reslice_position(self.mappers_mpr[plano], axis, pos_fisica)

        pane = self.vistas[plano]
        cam = pane.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()

        focal, pos = list(cam.GetFocalPoint()), list(cam.GetPosition())
        dist = pos[axis] - focal[axis]
        focal[axis], pos[axis] = pos_fisica, pos_fisica + dist

        cam.SetFocalPoint(focal)
        cam.SetPosition(pos)

        if hasattr(pane, 'lbl_mm'):
            pane.lbl_mm.setText(f"{pos_fisica:.1f} mm")

        pane.vtkWidget.GetRenderWindow().Render()
        return pos_fisica

    def update_preset(self, nome: str):
        if not self.volume_actor:
            return
        path = os.path.join(self.path_presets, f"{nome}.json")
        if not os.path.exists(path):
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                preset = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        self.color_function.RemoveAllPoints()
        self.opacity_function.RemoveAllPoints()
        for p in preset.get("colors", []):
            self.color_function.AddRGBPoint(*p)
        for p in preset.get("opacity", []):
            self.opacity_function.AddPoint(*p)

        thr = preset.get("threshold", 400)
        viewer_3d = self.vistas.get("3D")
        if viewer_3d and hasattr(viewer_3d, 'slider_threshold'):
            viewer_3d.slider_threshold.setValue(thr)

        self.volume_actor.GetProperty().SetShade(preset.get("shade", True))

        mode = vtk.VTK_COMPOSITE_BLEND if not preset.get("mip") else vtk.VTK_MAXIMUM_INTENSITY_BLEND
        self.volume_actor.GetMapper().SetBlendMode(mode)

        self.update_threshold(thr)
        if viewer_3d:
            viewer_3d.vtkWidget.GetRenderWindow().Render()

    def update_threshold(self, value: int):
        if not self.volume_actor:
            return
        self.opacity_function.RemoveAllPoints()
        self.opacity_function.AddPoint(value - 100, 0.0)
        self.opacity_function.AddPoint(value, 0.2)
        self.opacity_function.AddPoint(value + 500, 0.8)

        viewer_3d = self.vistas.get("3D")
        if viewer_3d:
            viewer_3d.vtkWidget.GetRenderWindow().Render()

    def update_3d_view(self, vista: str):
        viewer_3d = self.vistas.get("3D")
        if not viewer_3d:
            return

        ren = viewer_3d.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
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
            viewer_3d.vtkWidget.GetRenderWindow().Render()

    def clear_scene(self):
        self.volume_object = None
        self.volume_data = None
        for pane in self.vistas.values():
            rw = pane.vtkWidget.GetRenderWindow()
            ren = rw.GetRenderers().GetFirstRenderer()
            if ren:
                ren.RemoveAllViewProps()
            rw.Render()