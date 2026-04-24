import vtk
from pathlib import Path

class SegmentacaoEngine:
    def __init__(self):
        self.mask_data = None

    def gerar_mascara(self, volume_data: vtk.vtkImageData, threshold_value: int) -> vtk.vtkImageData:
        if not volume_data:
            return None

        thresh = vtk.vtkImageThreshold()
        thresh.SetInputData(volume_data)
        thresh.ThresholdByUpper(threshold_value)
        thresh.SetInValue(1)
        thresh.SetOutValue(0)
        thresh.Update()

        self.mask_data = thresh.GetOutput()
        return self.mask_data

    def exportar_stl(self, mask_data, caminho_saida, qualidade_index, callback_progresso=None):
        try:
            def update(msg, val):
                if callback_progresso:
                    callback_progresso(msg, val)

            # Mapeamento de qualidade para redução de polígonos:
            # 0: Alta (10% de redução - malha pesada e detalhada)
            # 1: Média (85% de redução - equilíbrio ideal)
            # 2: Baixa (95% de redução - malha muito leve)
            reducoes = {0: 0.10, 1: 0.85, 2: 0.95}
            fator_reducao = reducoes.get(qualidade_index, 0.85)

            # 1. Extração de Superfície
            update("Extraindo superfície (Flying Edges)...", 1)
            mesh_filter = vtk.vtkFlyingEdges3D()
            mesh_filter.SetInputData(mask_data)
            mesh_filter.SetValue(0, 0.5)
            mesh_filter.Update()

            # 2. Limpeza de Ruído
            update("Removendo artefatos pequenos...", 2)
            connectivity = vtk.vtkPolyDataConnectivityFilter()
            connectivity.SetInputConnection(mesh_filter.GetOutputPort())
            connectivity.SetExtractionModeToLargestRegion()
            connectivity.Update()

            # 3. Simplificação (Decimation) baseada na qualidade escolhida
            update(f"Simplificando malha ({int(fator_reducao*100)}% de redução)...", 3)
            decimator = vtk.vtkDecimatePro()
            decimator.SetInputConnection(connectivity.GetOutputPort())
            decimator.SetTargetReduction(fator_reducao)
            decimator.PreserveTopologyOn()
            decimator.Update()

            # 4. Suavização (Smoothing)
            update("Suavizando superfícies...", 4)
            smoother = vtk.vtkWindowedSincPolyDataFilter()
            smoother.SetInputConnection(decimator.GetOutputPort())
            smoother.SetNumberOfIterations(40)
            smoother.Update()

            # 5. Escrita de Arquivo
            update("Finalizando arquivo STL...", 5)
            writer = vtk.vtkSTLWriter()
            writer.SetFileName(str(caminho_saida))
            writer.SetInputData(smoother.GetOutput())
            writer.SetFileTypeToBinary()
            writer.Write()

            return True
        except Exception as e:
            print(f"Erro no processamento do volume: {e}")
            return False