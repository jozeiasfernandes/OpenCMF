import pydicom
import numpy as np
import vtk
from pathlib import Path
from typing import Optional, List, Tuple, Dict
from vtkmodules.util import numpy_support


class DicomEngine:
    """Motor de processamento para conversão de séries DICOM em volumes VTK 3D."""

    def __init__(self):
        self.volume_data: Optional[np.ndarray] = None
        self.vtk_volume: Optional[vtk.vtkImageData] = None
        self.spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.origin: List[float] = [0.0, 0.0, 0.0]

    def carregar_volume(self, caminho_pasta: str) -> Optional[vtk.vtkImageData]:
        """Atalho para carregar e retornar o objeto VTK diretamente."""
        sucesso, _ = self.carregar_pasta(caminho_pasta)
        return self.vtk_volume if sucesso else None

    def carregar_pasta(self, caminho_pasta: str) -> Tuple[bool, str]:
        """Lê, filtra e processa uma pasta de arquivos DICOM para gerar um volume 3D."""
        try:
            arquivos = self._listar_arquivos(caminho_pasta)
            if not arquivos:
                return False, "Nenhum arquivo DICOM encontrado."

            # 1. Filtragem Inicial (Ignora metadados inválidos ou Localizers)
            dataset_bruto = self._ler_metadados(arquivos)
            if not dataset_bruto:
                return False, "Dados de pixel ou geometria ausentes."

            # 2. Seleção da Melhor Série (Evita mistura de resoluções/estudos)
            dataset_valido = self._selecionar_melhor_serie(dataset_bruto)

            # 3. Ordenação Espacial (Baseado na coordenada Z)
            dataset_valido.sort(key=lambda x: float(x.ImagePositionPatient[2]))

            # 4. Configuração Geométrica
            self._configurar_geometria(dataset_valido)

            # 5. Processamento dos Pixels (Normalização e Empilhamento)
            self.volume_data = self._processar_pixels(dataset_valido)
            self.vtk_volume = self._numpy_to_vtk(self.volume_data)

            info = dataset_valido[0]
            return True, f"Sucesso: {info.get('SeriesDescription', 'Série s/ nome')} ({len(dataset_valido)} fatias)"

        except Exception as e:
            return False, f"Erro no Engine: {str(e)}"

    def _listar_arquivos(self, caminho: str) -> List[Path]:
        p = Path(caminho)
        return [f for f in p.iterdir() if f.is_file() and not f.name.startswith('.')]

    def _ler_metadados(self, arquivos: List[Path]) -> List[pydicom.dataset.FileDataset]:
        validos = []
        for f in arquivos:
            try:
                ds = pydicom.dcmread(str(f), stop_before_pixels=False)
                if hasattr(ds, 'pixel_array') and hasattr(ds, 'ImagePositionPatient'):
                    # Ignora fatias de referência (Localizers)
                    if "LOCALIZER" not in getattr(ds, "ImageType", []):
                        validos.append(ds)
            except:
                continue
        return validos

    def _selecionar_melhor_serie(self, datasets: List[pydicom.dataset.FileDataset]) -> List[
        pydicom.dataset.FileDataset]:
        """Agrupa fatias por Série + Resolução e retorna o maior grupo."""
        grupos: Dict[str, List] = {}
        for ds in datasets:
            chave = f"{ds.SeriesInstanceUID}_{ds.Rows}x{ds.Columns}"
            grupos.setdefault(chave, []).append(ds)

        chave_principal = max(grupos, key=lambda k: len(grupos[k]))
        return grupos[chave_principal]

    def _configurar_geometria(self, fatias: List[pydicom.dataset.FileDataset]):
        """Calcula o espaçamento entre fatias e a origem do volume."""
        ds0 = fatias[0]
        ps = ds0.PixelSpacing

        if len(fatias) > 1:
            z_spacing = abs(float(fatias[1].ImagePositionPatient[2]) - float(ds0.ImagePositionPatient[2]))
        else:
            z_spacing = float(ds0.get('SliceThickness', 1.0))

        self.spacing = (float(ps[0]), float(ps[1]), float(z_spacing))
        self.origin = [float(x) for x in ds0.ImagePositionPatient]

    def _processar_pixels(self, fatias: List[pydicom.dataset.FileDataset]) -> np.ndarray:
        """Aplica Rescale Slope/Intercept e empilha as fatias em um array 3D."""
        volume = []
        for ds in fatias:
            img = ds.pixel_array.astype(np.int16)

            slope = float(getattr(ds, 'RescaleSlope', 1))
            intercept = float(getattr(ds, 'RescaleIntercept', 0))

            if slope != 1 or intercept != 0:
                img = (img * slope) + intercept

            volume.append(img)
        return np.stack(volume)

    def _numpy_to_vtk(self, nparray: np.ndarray) -> vtk.vtkImageData:
        """Converte o array NumPy para o formato vtkImageData."""
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