import pydicom
import numpy as np
from pathlib import Path
import vtk
from typing import Optional, List, Tuple

try:
    from vtkmodules.util import numpy_support
except ImportError:
    try:
        from vtk.util import numpy_support
    except ImportError:
        import vtk.util.numpy_support as numpy_support


class DicomEngine:
    def __init__(self):
        self.volume_data: Optional[np.ndarray] = None
        self.vtk_volume: Optional[vtk.vtkImageData] = None
        self.spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.origin: List[float] = [0.0, 0.0, 0.0]

    def carregar_volume(self, caminho_pasta: str) -> Optional[vtk.vtkImageData]:
        sucesso, _ = self.carregar_pasta(caminho_pasta)
        return self.vtk_volume if sucesso else None

    def carregar_pasta(self, caminho_pasta: str) -> Tuple[bool, str]:
        try:
            caminho = Path(caminho_pasta)
            arquivos = list(caminho.glob("*.dcm"))
            if not arquivos:
                arquivos = [f for f in caminho.iterdir() if f.is_file() and not f.name.startswith('.')]

            if not arquivos:
                return False, "Nenhum arquivo DICOM encontrado no diretório."

            dataset_valido = []
            shape_referencia = None

            for f in arquivos:
                try:
                    ds = pydicom.dcmread(str(f))
                    if not hasattr(ds, 'pixel_array'):
                        continue

                    current_shape = ds.pixel_array.shape
                    if shape_referencia is None:
                        shape_referencia = current_shape

                    if current_shape == shape_referencia:
                        dataset_valido.append(ds)
                except Exception:
                    continue

            if not dataset_valido:
                return False, "Não foi possível extrair dados de pixel."

            dataset_valido.sort(key=lambda x: float(x.ImagePositionPatient[2]))

            ds0 = dataset_valido[0]
            ps = ds0.PixelSpacing

            if len(dataset_valido) > 1:
                z_spacing = abs(float(dataset_valido[1].ImagePositionPatient[2]) - float(ds0.ImagePositionPatient[2]))
            else:
                z_spacing = float(ds0.get('SliceThickness', 1.0))

            self.spacing = (float(ps[0]), float(ps[1]), z_spacing)
            self.origin = [float(x) for x in ds0.ImagePositionPatient]

            volume_list = []
            for ds in dataset_valido:
                img2d = ds.pixel_array.astype(np.int16)
                slope = float(getattr(ds, 'RescaleSlope', 1))
                intercept = float(getattr(ds, 'RescaleIntercept', 0))

                if slope != 1 or intercept != 0:
                    img2d = (img2d * slope) + intercept

                volume_list.append(img2d)

            self.volume_data = np.stack(volume_list)
            self.vtk_volume = self._numpy_to_vtk(self.volume_data)

            return True, f"{len(dataset_valido)} fatias carregadas."

        except Exception as e:
            return False, f"Erro: {str(e)}"

    def _numpy_to_vtk(self, nparray: np.ndarray) -> vtk.vtkImageData:
        depth, height, width = nparray.shape

        vtk_array = numpy_support.numpy_to_vtk(
            num_array=nparray.flatten(),
            deep=True,
            array_type=vtk.VTK_SHORT
        )

        img_data = vtk.vtkImageData()
        img_data.SetDimensions(width, height, depth)
        img_data.SetSpacing(self.spacing)
        img_data.SetOrigin(self.origin)
        img_data.GetPointData().SetScalars(vtk_array)

        return img_data