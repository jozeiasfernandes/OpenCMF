import pydicom
import numpy as np
from pathlib import Path
import vtk
from vtk.util import numpy_support
from typing import Optional

class DicomEngine:
    def __init__(self):
        self.volume_data = None  # Array NumPy
        self.vtk_volume = None  # Objeto vtkImageData
        self.spacing = (1.0, 1.0, 1.0)
        self.origin = (0.0, 0.0, 0.0)

    def carregar_volume(self, caminho_pasta: str) -> Optional[vtk.vtkImageData]:
        """
        MÉTODO PARA SEGMENTAÇÃO: Retorna o objeto VTK diretamente.
        Não quebra os outros módulos pois é um método novo.
        """
        sucesso, _ = self.carregar_pasta(caminho_pasta)
        if sucesso:
            return self.vtk_volume
        return None

    def carregar_pasta(self, caminho_pasta: str):
        """MÉTODO ORIGINAL: Mantido exatamente como a Tomografia espera."""
        try:
            caminho = Path(caminho_pasta)
            arquivos = list(caminho.glob("*.dcm"))

            if not arquivos:
                return False, "Nenhum arquivo DICOM encontrado."

            # 1. Ler fatias e ordenar
            fatias = [pydicom.dcmread(str(f)) for f in arquivos]
            fatias.sort(key=lambda x: float(x.ImagePositionPatient[2]))

            # 2. Extrair propriedades espaciais
            ps = fatias[0].PixelSpacing
            thickness = fatias[0].SliceThickness if 'SliceThickness' in fatias[0] else 1.0
            self.spacing = (float(ps[0]), float(ps[1]), float(thickness))
            self.origin = [float(x) for x in fatias[0].ImagePositionPatient]

            # 3. Empilhar os pixels (HU)
            volume_list = []
            for f in fatias:
                img2d = f.pixel_array.astype(np.int16)
                slope = getattr(f, 'RescaleSlope', 1)
                intercept = getattr(f, 'RescaleIntercept', 0)
                if slope != 1 or intercept != 0:
                    img2d = img2d * slope + intercept
                volume_list.append(img2d)

            self.volume_data = np.stack(volume_list)

            # 4. Converter NumPy para vtkImageData
            self.vtk_volume = self._numpy_to_vtk(self.volume_data)
            return True, f"{len(fatias)} fatias carregadas com sucesso."
        except Exception as e:
            return False, f"Erro ao carregar DICOM: {str(e)}"

    def _numpy_to_vtk(self, nparray):
        if not nparray.flags['C_CONTIGUOUS']:
            nparray = np.ascontiguousarray(nparray)

        vtk_array = numpy_support.numpy_to_vtk(num_array=nparray.flatten(), deep=True, array_type=vtk.VTK_SHORT)
        img_data = vtk.vtkImageData()
        depth, height, width = nparray.shape
        img_data.SetDimensions(width, height, depth)
        img_data.SetSpacing(self.spacing)
        img_data.SetOrigin(0, 0, 0)
        img_data.GetPointData().SetScalars(vtk_array)
        return img_data