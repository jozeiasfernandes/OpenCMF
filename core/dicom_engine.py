import pydicom
import numpy as np
from pathlib import Path
import vtk
from vtk.util import numpy_support


class DicomEngine:
    def __init__(self):
        self.volume_data = None
        self.vtk_volume = None
        self.spacing = (1.0, 1.0, 1.0)
        self.origin = (0.0, 0.0, 0.0)

    def carregar_pasta(self, caminho_pasta: str):
        caminho = Path(caminho_pasta)
        arquivos = list(caminho.glob("*.dcm"))

        if not arquivos:
            return False, "Nenhum arquivo DICOM encontrado."

        fatias = [pydicom.dcmread(f) for f in arquivos]
        fatias.sort(key=lambda x: float(x.ImagePositionPatient[2]))

        self._configurar_espacamento_e_origem(fatias)
        self.volume_data = self._extrair_pixels_hu(fatias)
        self.vtk_volume = self._converte_para_vtk(self.volume_data)

        return True, f"{len(fatias)} fatias carregadas com sucesso."

    def _configurar_espacamento_e_origem(self, fatias):
        ps = fatias[0].PixelSpacing

        distancia_z = 1.0
        if len(fatias) > 1:
            distancia_z = abs(float(fatias[1].ImagePositionPatient[2]) - float(fatias[0].ImagePositionPatient[2]))
        else:
            distancia_z = float(getattr(fatias[0], 'SliceThickness', 1.0))

        self.spacing = (float(ps[0]), float(ps[1]), distancia_z)
        self.origin = [float(x) for x in fatias[0].ImagePositionPatient]

    def _extrair_pixels_hu(self, fatias):
        volume_list = []
        for f in fatias:
            img2d = f.pixel_array.astype(np.int16)
            slope = getattr(f, 'RescaleSlope', 1)
            intercept = getattr(f, 'RescaleIntercept', 0)

            if slope != 1 or intercept != 0:
                img2d = (img2d * slope) + intercept

            volume_list.append(img2d)

        return np.stack(volume_list)

    def _converte_para_vtk(self, nparray):
        if not nparray.flags['C_CONTIGUOUS']:
            nparray = np.ascontiguousarray(nparray)

        vtk_array = numpy_support.numpy_to_vtk(
            num_array=nparray.flatten(),
            deep=True,
            array_type=vtk.VTK_SHORT
        )

        img_data = vtk.vtkImageData()
        slices, height, width = nparray.shape

        img_data.SetDimensions(width, height, slices)
        img_data.SetSpacing(self.spacing)
        img_data.SetOrigin(self.origin)
        img_data.GetPointData().SetScalars(vtk_array)

        return img_data