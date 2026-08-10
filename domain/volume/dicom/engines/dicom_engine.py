import pydicom
import numpy as np
import vtk
from vtkmodules.util import numpy_support

from pathlib import Path
from typing import Optional, List, Dict, Any

from domain.volume.models.volume_model import Volume
from domain.volume.dicom.validators.dicom_validator import DicomValidator


class DicomEngine:
    def __init__(self, event_bus: Optional[Any] = None):
        self._current_volume: Optional[Volume] = None
        self.last_spacing = (1.0, 1.0, 1.0)
        self.last_origin = (0.0, 0.0, 0.0)
        self.validator = DicomValidator(event_bus=event_bus)

    def process_to_scene_object(self, caminho_pasta: str) -> Optional[Dict[str, Any]]:
        volume_model = self.load_volume(caminho_pasta)
        if not volume_model or not volume_model.is_valid:
            return None

        return {
            "metadata": {
                "mesh_data": volume_model.vtk_data,
                "volume_model": volume_model,
                "source_path": caminho_pasta
            },
            "transforms": {
                "position": self.last_origin,
                "scale": [1.0, 1.0, 1.0]
            }
        }

    def load_volume(self, caminho_pasta: str) -> Optional[Volume]:
        path_obj = Path(caminho_pasta)

        # 1. Validação prévia com o DicomValidator
        validacao = self.validator.validate_directory(path_obj)
        if not validacao.get("sucesso", False):
            return None

        arquivos = self._list_files(caminho_pasta)
        dataset = self._read_metadata(arquivos)

        if not dataset:
            return None

        dataset = self._select_best_series(dataset)
        if not dataset:
            return None

        # Validação preventiva de atributos DICOM essenciais
        if not self._validate_dicom_attributes(dataset):
            return None

        # Ordena pelas coordenadas espaciais Z (ImagePositionPatient[2])
        dataset.sort(key=lambda x: float(x.ImagePositionPatient[2]))

        self._configure_geometry(dataset)
        volume_data = self._process_pixels(dataset)

        # Converte para vtkImageData
        vtk_img = self._numpy_to_vtk(volume_data)

        # 2. Criação correta do modelo Volume usando image_data
        self._current_volume = Volume(image_data=vtk_img)
        self._current_volume.source_path = caminho_pasta
        self._current_volume.name = "Exame DICOM / TC"

        return self._current_volume

    def _validate_dicom_attributes(self, dataset: List[pydicom.dataset.FileDataset]) -> bool:
        """Valida se os atributos DICOM essenciais estão presentes nas fatias iniciais."""
        required_attrs = ['ImagePositionPatient', 'PixelSpacing', 'Rows', 'Columns']
        for ds in dataset[:min(3, len(dataset))]:
            for attr in required_attrs:
                if not hasattr(ds, attr):
                    return False
        return True

    def _configure_geometry(self, fatias: List[pydicom.dataset.FileDataset]):
        ds0 = fatias[0]

        if not hasattr(ds0, 'PixelSpacing'):
            self.last_spacing = (1.0, 1.0, 1.0)
        else:
            ps = ds0.PixelSpacing
            self.last_spacing = (float(ps[0]), float(ps[1]), 1.0)

        if len(fatias) > 1:
            try:
                z1 = float(fatias[0].ImagePositionPatient[2])
                z2 = float(fatias[1].ImagePositionPatient[2])
                z_spacing = abs(z2 - z1)
            except (AttributeError, IndexError):
                z_spacing = float(getattr(ds0, 'SliceThickness', 1.0))
        else:
            z_spacing = float(getattr(ds0, 'SliceThickness', 1.0))

        self.last_spacing = (self.last_spacing[0], self.last_spacing[1], z_spacing)

        try:
            self.last_origin = tuple(float(x) for x in ds0.ImagePositionPatient)
        except (AttributeError, TypeError):
            self.last_origin = (0.0, 0.0, 0.0)

    def _process_pixels(self, fatias: List[pydicom.dataset.FileDataset]) -> np.ndarray:
        shape = (len(fatias), fatias[0].Rows, fatias[0].Columns)
        volume = np.zeros(shape, dtype=np.float32)

        for i, ds in enumerate(fatias):
            slope = float(getattr(ds, 'RescaleSlope', 1.0))
            intercept = float(getattr(ds, 'RescaleIntercept', 0.0))

            pixel_array = ds.pixel_array.astype(np.float32)
            volume[i] = pixel_array * slope + intercept

        return volume

    def _numpy_to_vtk(self, nparray: np.ndarray) -> vtk.vtkImageData:
        vtk_array = numpy_support.numpy_to_vtk(
            nparray.ravel(order='C'), deep=True, array_type=vtk.VTK_FLOAT
        )

        img_data = vtk.vtkImageData()
        img_data.SetDimensions(nparray.shape[2], nparray.shape[1], nparray.shape[0])
        img_data.SetSpacing(self.last_spacing)
        img_data.SetOrigin(self.last_origin)
        img_data.GetPointData().SetScalars(vtk_array)
        return img_data

    def _list_files(self, caminho: str) -> List[Path]:
        return [
            f for f in Path(caminho).rglob("*")
            if f.is_file() and not f.name.startswith('.')
        ]

    def _read_metadata(self, arquivos: List[Path]) -> List[pydicom.dataset.FileDataset]:
        result = []
        for f in arquivos:
            try:
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

    def _select_best_series(self, datasets: List[pydicom.dataset.FileDataset]) -> List[
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

        chave_principal = max(grupos, key=lambda k: len(grupos[k]))
        return grupos[chave_principal]

    @property
    def current_volume(self) -> Optional[Volume]:
        return self._current_volume

    def load_folder(self, caminho_pasta: str):
        """Carrega a pasta DICOM e retorna o status de sucesso e o volume ou mensagem de erro."""
        try:
            volume = self.load_volume(caminho_pasta)
            if volume and getattr(volume, "is_valid", True):
                return True, volume
            return False, "Falha ao carregar ou validar o volume DICOM."
        except Exception as e:
            return False, str(e)