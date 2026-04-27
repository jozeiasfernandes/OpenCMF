import vtk
from .lut_presets import LUTPresets


class LUTManager:
    @staticmethod
    def get_vtk_lut(name: str) -> vtk.vtkLookupTable:
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfTableValues(256)

        preset_name = name if name in LUTPresets.PRESETS else "Grayscale"
        stops = LUTPresets.PRESETS[preset_name]

        color_func = vtk.vtkColorTransferFunction()

        for pos, hex_val in stops:
            r = int(hex_val[1:3], 16) / 255.0
            g = int(hex_val[3:5], 16) / 255.0
            b = int(hex_val[5:7], 16) / 255.0
            color_func.AddRGBPoint(pos, r, g, b)

        for i in range(256):
            rgb = color_func.GetColor(i / 255.0)
            lut.SetTableValue(i, *rgb, 1.0)

        lut.Build()
        return lut