import pydicom
import numpy as np
import vtk
from pathlib import Path
from typing import Optional, List, Dict, Any
from vtkmodules.util import numpy_support


class DicomEngine:
    def __init__(self):
        self._vtk_volume: Optional[vtk.vtkImageData] = None
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
        if not dataset:
            return None

        # Ordena pelas coordenadas espaciais Z (ImagePositionPatient[2])
        dataset.sort(key=lambda x: float(x.ImagePositionPatient[2]))

        self._configurar_geometria(dataset)
        volume_data = self._processar_pixels(dataset)

        # Converte e armazena corretamente no estado interno da engine
        self._vtk_volume = self._numpy_to_vtk(volume_data)
        return self._vtk_volume

    def _configurar_geometria(self, fatias: List[pydicom.dataset.FileDataset]):
        ds0 = fatias[0]
        ps = ds0.PixelSpacing

        z_spacing = abs(
            float(fatias[1].ImagePositionPatient[2]) - float(ds0.ImagePositionPatient[2])
        ) if len(fatias) > 1 else float(getattr(ds0, 'SliceThickness', 1.0))

        self.last_spacing = (float(ps[0]), float(ps[1]), float(z_spacing))
        self.last_origin = tuple(float(x) for x in ds0.ImagePositionPatient)

    def _processar_pixels(self, fatias: List[pydicom.dataset.FileDataset]) -> np.ndarray:
        shape = (len(fatias), fatias[0].Rows, fatias[0].Columns)
        volume = np.zeros(shape, dtype=np.float32)

        for i, ds in enumerate(fatias):
            slope = float(getattr(ds, 'RescaleSlope', 1.0))
            intercept = float(getattr(ds, 'RescaleIntercept', 0.0))

            pixel_array = ds.pixel_array.astype(np.float32)
            volume[i] = pixel_array * slope + intercept

        return volume

    def _numpy_to_vtk(self, nparray: np.ndarray) -> vtk.vtkImageData:
        # Achatamento compatível com a ordem C do numpy (Z, Y, X)
        vtk_array = numpy_support.numpy_to_vtk(
            nparray.ravel(order='C'), deep=True, array_type=vtk.VTK_FLOAT
        )

        img_data = vtk.vtkImageData()
        # Dimensões no VTK: (Columns, Rows, Slices) -> (X, Y, Z)
        img_data.SetDimensions(nparray.shape[2], nparray.shape[1], nparray.shape[0])
        img_data.SetSpacing(self.last_spacing)
        img_data.SetOrigin(self.last_origin)
        img_data.GetPointData().SetScalars(vtk_array)
        return img_data

    def _listar_arquivos(self, caminho: str) -> List[Path]:
        # Alterado para rglob para suportar estruturas de pastas aninhadas em exames DICOM
        return [
            f for f in Path(caminho).rglob("*")
            if f.is_file() and not f.name.startswith('.')
        ]

    def _ler_metadados(self, arquivos: List[Path]) -> List[pydicom.dataset.FileDataset]:
        result = []
        for f in arquivos:
            try:
                # Otimização: Valida o cabeçalho DICM antes de carregar o arquivo inteiro
                with open(f, 'rb') as file_obj:
                    file_obj.seek(128)
                    if file_obj.read(4) != b"DICM":
                        continue

                ds = pydicom.dcmread(str(f))
                if hasattr(ds, "pixel_array") and hasattr(ds, "ImagePositionPatient"):
                    result.append(ds)
            except Exception:
                continue
        return result

    def _selecionar_melhor_serie(self, datasets: List[pydicom.dataset.FileDataset]) -> List[
        pydicom.dataset.FileDataset]:
        if not datasets:
            return []

        grupos: Dict[str, List] = {}
        for ds in datasets:
            series_uid = getattr(ds, "SeriesInstanceUID", "unknown")
            chave = f"{series_uid}_{ds.Rows}x{ds.Columns}"
            grupos.setdefault(chave, []).append(ds)

        if not grupos:
            return []

        # Seleciona a série que possui o maior número de fatias (exame completo)
        chave_principal = max(grupos, key=lambda k: len(grupos[k]))
        return grupos[chave_principal]

    @property
    def vtk_volume(self) -> Optional[vtk.vtkImageData]:
        return self._vtk_volume