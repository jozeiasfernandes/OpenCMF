import vtk
from .lut_presets import LUTPresets


class LUTManager:
    @staticmethod
    def get_vtk_lut(name: str) -> vtk.vtkLookupTable:
        """
        Converte um preset do LUTPresets em um vtkLookupTable utilizável pelo VTK.
        """
        lut = vtk.vtkLookupTable()

        # Se o preset não existir, retorna um grayscale padrão
        preset_name = name if name in LUTPresets.PRESETS else "Grayscale"
        stops = LUTPresets.PRESETS[preset_name]

        # Configuramos o número de cores (256 é o padrão para imagens 8-bit/DICOM)
        lut.SetNumberOfTableValues(256)

        # Criamos uma função de transferência de cor para interpolar os stops
        color_func = vtk.vtkColorTransferFunction()
        for pos, hex_color in stops:
            # Converter Hex para RGB (0.0 a 1.0)
            r = int(hex_color[1:3], 16) / 255.0
            g = int(hex_color[3:5], 16) / 255.0
            b = int(hex_color[5:7], 16) / 255.0
            color_func.AddRGBPoint(pos, r, g, b)

        # Preenchemos a tabela do VTK com os valores interpolados
        for i in range(256):
            rgb = color_func.GetColor(i / 255.0)
            lut.SetTableValue(i, rgb[0], rgb[1], rgb[2], 1.0)

        lut.Build()
        return lut