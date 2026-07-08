import pydicom
import numpy as np
import vtk
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from vtkmodules.util import numpy_support


class DicomEngine:
    def __init__(self):
        self.last_spacing = (1.0, 1.0, 1.0)
        self.last_origin = (0.0, 0.0, 0.0)

    def processar_para_scene_object(self, caminho_pasta: str) -> Optional[Dict[str, Any]]:
        vtk_volume = self.carregar_volume(caminho_pasta)
        if not vtk_volume:
            return None

        return {
            "metadata": {
                "mesh_data": vtk_volume,
                "source_path": caminho_pasta
            },
            "transforms": {
                "position": self.last_origin,
                "scale": [1.0, 1.0, 1.0]
            }
        }

    def carregar_volume(self, caminho_pasta: str) -> Optional[vtk.vtkImageData]:
        arquivos = self._listar_arquivos(caminho_pasta)
        dataset = self._ler_metadados(arquivos)

        if not dataset:
            return None

        dataset = self._selecionar_melhor_serie(dataset)
        dataset.sort(key=lambda x: float(x.ImagePositionPatient[2]))

        self._configurar_geometria(dataset)
        volume_data = self._processar_pixels(dataset)

        return self._numpy_to_vtk(volume_data)

    def _configurar_geometria(self, fatias: List[pydicom.dataset.FileDataset]):
        ds0 = fatias[0]
        ps = ds0.PixelSpacing

        z_spacing = abs(
            float(fatias[1].ImagePositionPatient[2]) - float(ds0.ImagePositionPatient[2])
        ) if len(fatias) > 1 else float(ds0.get('SliceThickness', 1.0))

        self.last_spacing = (float(ps[0]), float(ps[1]), float(z_spacing))
        self.last_origin = tuple(float(x) for x in ds0.ImagePositionPatient)

    def _processar_pixels(self, fatias: List[pydicom.dataset.FileDataset]) -> np.ndarray:
        shape = (len(fatias), fatias[0].Rows, fatias[0].Columns)
        volume = np.zeros(shape, dtype=np.float32)

        for i, ds in enumerate(fatias):
            slope = float(getattr(ds, 'RescaleSlope', 1))
            intercept = float(getattr(ds, 'RescaleIntercept', 0))
            volume[i] = ds.pixel_array.astype(np.float32) * slope + intercept

        return volume

    def _numpy_to_vtk(self, nparray: np.ndarray) -> vtk.vtkImageData:
        vtk_array = numpy_support.numpy_to_vtk(
            nparray.flatten(), deep=True, array_type=vtk.VTK_FLOAT
        )

        img_data = vtk.vtkImageData()
        img_data.SetDimensions(nparray.shape[2], nparray.shape[1], nparray.shape[0])
        img_data.SetSpacing(self.last_spacing)
        img_data.SetOrigin(self.last_origin)
        img_data.GetPointData().SetScalars(vtk_array)
        return img_data

    def _listar_arquivos(self, caminho: str) -> List[Path]:
        return [
            f for f in Path(caminho).iterdir()
            if f.is_file() and not f.name.startswith('.')
        ]

    def _ler_metadados(self, arquivos: List[Path]) -> List[pydicom.dataset.FileDataset]:
        result = []
        for f in arquivos:
            try:
                ds = pydicom.dcmread(str(f), stop_before_pixels=True)
                if ds.get('pixel_array') is not None:
                    result.append(pydicom.dcmread(str(f)))
            except:
                continue
        return result

    def _selecionar_melhor_serie(self, datasets: List[pydicom.dataset.FileDataset]) -> List[pydicom.dataset.FileDataset]:
        if not datasets:
            return []

        grupos: Dict[str, List] = {}
        for ds in datasets:
            chave = f"{ds.SeriesInstanceUID}_{ds.Rows}x{ds.Columns}"
            grupos.setdefault(chave, []).append(ds)

        if not grupos:
            return []

        chave_principal = max(grupos, key=lambda k: len(grupos[k]))
        return grupos[chave_principal]