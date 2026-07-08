import vtk
from pathlib import Path
from typing import Optional, Callable, Any
from core.scene.events.scene_events import SceneEvents


class SegmentacaoEngine:
    """
    Serviço de segmentação. Não mantém estado interno para evitar
    conflitos em processamento assíncrono.
    """

    def __init__(self, event_bus: Any = None):
        self.event_bus = event_bus

    def gerar_mascara(self, volume_data: vtk.vtkImageData, threshold_value: int) -> vtk.vtkImageData:
        if not volume_data:
            return None

        thresh = vtk.vtkImageThreshold()
        thresh.SetInputData(volume_data)
        thresh.ThresholdByUpper(threshold_value)
        thresh.SetInValue(1)
        thresh.SetOutValue(0)
        thresh.Update()

        # Retorna uma cópia para garantir que o pipeline não seja modificado externamente
        output = vtk.vtkImageData()
        output.DeepCopy(thresh.GetOutput())
        return output

    def exportar_stl(self, mask_data: vtk.vtkImageData, caminho_saida: Path,
                     qualidade_index: int, callback_progresso: Optional[Callable] = None) -> bool:
        try:
            update = lambda msg, val: callback_progresso(msg, val) if callback_progresso else None

            fator_reducao = {0: 0.10, 1: 0.85, 2: 0.95}.get(qualidade_index, 0.85)

            # 1. Extração
            update("Extraindo superfície...", 1)
            mesh = vtk.vtkFlyingEdges3D()
            mesh.SetInputData(mask_data)
            mesh.SetValue(0, 0.5)

            # 2. Conectividade
            update("Limpando ruídos...", 2)
            conn = vtk.vtkPolyDataConnectivityFilter()
            conn.SetInputConnection(mesh.GetOutputPort())
            conn.SetExtractionModeToLargestRegion()

            # 3. Simplificação
            update("Simplificando malha...", 3)
            decimator = vtk.vtkDecimatePro()
            decimator.SetInputConnection(conn.GetOutputPort())
            decimator.SetTargetReduction(fator_reducao)
            decimator.PreserveTopologyOn()

            # 4. Suavização
            update("Suavizando...", 4)
            smoother = vtk.vtkWindowedSincPolyDataFilter()
            smoother.SetInputConnection(decimator.GetOutputPort())
            smoother.SetNumberOfIterations(40)
            smoother.BoundarySmoothingOn()
            smoother.FeatureEdgeSmoothingOn()
            smoother.Update()

            # 5. Escrita
            update("Salvando arquivo...", 5)
            writer = vtk.vtkSTLWriter()
            writer.SetFileName(str(caminho_saida))
            writer.SetInputData(smoother.GetOutput())
            writer.SetFileTypeToBinary()
            writer.Write()

            return True

        except Exception as e:
            if self.event_bus:
                self.event_bus.emit(SceneEvents.ERROR_OCCURRED, message=f"Falha na exportação: {str(e)}")
            return False