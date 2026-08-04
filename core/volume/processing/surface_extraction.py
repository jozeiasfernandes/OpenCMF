import vtk
from typing import Optional, Callable


class SurfaceExtraction:
    """
    Processo de derivação responsável por extrair superfícies poligonais (malhas 3D)
    a partir de dados volumétricos ou máscaras segmentadas.
    """

    @staticmethod
    def extrair_malha(
        mask_data: vtk.vtkImageData,
        qualidade_index: int = 1,
        callback_progresso: Optional[Callable[[str, int], None]] = None
    ) -> Optional[vtk.vtkPolyData]:
        """
        Executa o pipeline de Marching Cubes (Flying Edges), limpeza de conectividade,
        decimação (simplificação) e suavização da malha poligonal.
        """
        if not mask_data:
            return None

        def _update(msg: str, val: int):
            if callback_progresso:
                callback_progresso(msg, val)

        try:
            # Mapeamento do fator de redução com base no índice de qualidade
            # 0: Baixa qualidade (mais leve/rápido), 1: Padrão, 2: Alta qualidade (mais detalhado)
            fator_reducao = {0: 0.10, 1: 0.85, 2: 0.95}.get(qualidade_index, 0.85)

            # 1. Extração de Superfície (Marching Cubes moderno via Flying Edges)
            _update("Extraindo superfície tridimensional...", 10)
            mesh = vtk.vtkFlyingEdges3D()
            mesh.SetInputData(mask_data)
            mesh.SetValue(0, 0.5)
            mesh.Update()

            # 2. Conectividade (Remove ilhas e ruídos desconectados)
            _update("Limpando ruídos e ilhas isoladas...", 30)
            conn = vtk.vtkPolyDataConnectivityFilter()
            conn.SetInputConnection(mesh.GetOutputPort())
            conn.SetExtractionModeToLargestRegion()
            conn.Update()

            # 3. Simplificação de malha (Decimação)
            _update("Simplificando malha poligonal...", 60)
            decimator = vtk.vtkDecimatePro()
            decimator.SetInputConnection(conn.GetOutputPort())
            decimator.SetTargetReduction(fator_reducao)
            decimator.PreserveTopologyOn()
            decimator.Update()

            # 4. Suavização (Windowed Sinc PolyData Filter)
            _update("Aplicando suavização na malha...", 85)
            smoother = vtk.vtkWindowedSincPolyDataFilter()
            smoother.SetInputConnection(decimator.GetOutputPort())
            smoother.SetNumberOfIterations(40)
            smoother.BoundarySmoothingOn()
            smoother.FeatureEdgeSmoothingOn()
            smoother.Update()

            _update("Extração de superfície concluída com sucesso!", 100)
            return smoother.GetOutput()

        except Exception as e:
            if callback_progresso:
                callback_progresso(f"Erro na extração: {str(e)}", -1)
            return None