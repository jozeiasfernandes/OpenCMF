import pydicom
import numpy as np
from pathlib import Path
import vtk
from vtk.util import numpy_support


class DicomEngine:
    def __init__(self):
        self.volume_data = None  # Array NumPy
        self.vtk_volume = None  # Objeto vtkImageData
        self.spacing = (1.0, 1.0, 1.0)
        self.origin = (0.0, 0.0, 0.0)

    def carregar_pasta(self, caminho_pasta: str):
        """Lê os arquivos DICOM, ordena por posição e gera o volume VTK."""
        caminho = Path(caminho_pasta)
        arquivos = list(caminho.glob("*.dcm"))

        if not arquivos:
            return False, "Nenhum arquivo DICOM encontrado."

        # 1. Ler fatias e ordenar pela posição espacial (ImagePositionPatient Z)
        fatias = [pydicom.dcmread(f) for f in arquivos]
        fatias.sort(key=lambda x: float(x.ImagePositionPatient[2]))

        # 2. Extrair propriedades espaciais
        # PixelSpacing: [distância entre linhas, distância entre colunas]
        ps = fatias[0].PixelSpacing
        # SliceThickness ou diferença entre ImagePositionPatient[2]
        thickness = fatias[0].SliceThickness if 'SliceThickness' in fatias[0] else 1.0
        self.spacing = (float(ps[0]), float(ps[1]), float(thickness))
        self.origin = [float(x) for x in fatias[0].ImagePositionPatient]

        # 3. Empilhar os pixels (Rescale Slope/Intercept convertem para unidades Hounsfield)
        volume_list = []
        for f in fatias:
            img2d = f.pixel_array.astype(np.int16)
            # Converter para HU: valor * slope + intercept
            slope = getattr(f, 'RescaleSlope', 1)
            intercept = getattr(f, 'RescaleIntercept', 0)
            if slope != 1 or intercept != 0:
                img2d = img2d * slope + intercept
            volume_list.append(img2d)

        self.volume_data = np.stack(volume_list)

        # 4. Converter NumPy para vtkImageData (Onde a mágica do VTK acontece)
        self.vtk_volume = self._numpy_to_vtk(self.volume_data)
        return True, f"{len(fatias)} fatias carregadas com sucesso."

    def _numpy_to_vtk(self, nparray):
        # 1. Garante que o array seja contíguo na memória (crucial para evitar o "chuvisco")
        # Usamos order='C' para alinhar com o padrão esperado pelo VTK
        if not nparray.flags['C_CONTIGUOUS']:
            nparray = np.ascontiguousarray(nparray)

        # 2. Converte para VTK array
        vtk_array = numpy_support.numpy_to_vtk(num_array=nparray.flatten(), deep=True, array_type=vtk.VTK_SHORT)

        img_data = vtk.vtkImageData()

        # IMPORTANTE: A ordem das dimensões no VTK é (X, Y, Z)
        # No NumPy geralmente é (Z, Y, X) ou (slices, height, width)
        depth, height, width = nparray.shape
        img_data.SetDimensions(width, height, depth)

        # Define o espaçamento (pixel spacing e slice thickness)
        img_data.SetSpacing(self.spacing)  # Ex: (0.5, 0.5, 1.0)
        img_data.SetOrigin(0, 0, 0)
        img_data.GetPointData().SetScalars(vtk_array)

        return img_data