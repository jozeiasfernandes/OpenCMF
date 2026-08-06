import vtk
from pathlib import Path
from typing import Optional, Callable, Any
from domain.volume.segmentation.strategies.threshold import ThresholdStrategy
from domain.volume.processing.surface_extraction import SurfaceExtraction
from domain.volume.exporters.mesh_exporters import MeshExporter

try:
    from core.scene.events.scene_events import SceneEvents
except ImportError:
    SceneEvents = None


class ThresholdSegmentationEngine:
    """
    Motor de segmentação baseado em limiarização de intensidade (Thresholding).
    Não mantém estado interno para evitar conflitos em processamento assíncrono.
    """

    def __init__(self, event_bus: Any = None):
        self.event_bus = event_bus

    def gerar_mascara(self, volume_data: vtk.vtkImageData, threshold_value: float) -> Optional[vtk.vtkImageData]:
        """
        Gera uma máscara binária aplicando a estratégia de limiarização sobre o volume.
        """
        return ThresholdStrategy.executar(volume_data, lower_threshold=threshold_value)

    def exportar_stl(
        self,
        mask_data: vtk.vtkImageData,
        caminho_saida: Path,
        qualidade_index: int = 1,
        callback_progresso: Optional[Callable[[str, int], None]] = None
    ) -> bool:
        """
        Coordena o pipeline completo de conversão da máscara em malha 3D e exportação para arquivo STL.
        """
        try:
            # 1. Extração e processamento da malha geométrica a partir da máscara
            polydata = SurfaceExtraction.extrair_malha(
                mask_data=mask_data,
                qualidade_index=qualidade_index,
                callback_progresso=callback_progresso
            )

            if not polydata:
                raise ValueError("Falha ao gerar os dados geométricos da superfície.")

            # 2. Persistência e exportação do arquivo STL
            sucesso = MeshExporter.salvar_stl(
                polydata=polydata,
                caminho_saida=caminho_saida,
                binario=True,
                callback_progresso=callback_progresso
            )

            return sucesso

        except Exception as e:
            if self.event_bus and SceneEvents and hasattr(SceneEvents, "ERROR_OCCURRED"):
                self.event_bus.emit(SceneEvents.ERROR_OCCURRED, message=f"Falha na exportação: {str(e)}")
            elif callback_progresso:
                callback_progresso(f"Erro: {str(e)}", -1)
            return False