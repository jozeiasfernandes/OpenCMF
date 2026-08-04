import vtk
from typing import Optional


class ThresholdStrategy:
    """
    Estratégia de segmentação baseada em limiarização (Thresholding) de intensidades de voxels.
    """

    @staticmethod
    def executar(volume_data: vtk.vtkImageData, lower_threshold: float, upper_threshold: Optional[float] = None) -> \
    Optional[vtk.vtkImageData]:
        """
        Gera uma máscara binária a partir de um intervalo de limiar de intensidade.
        """
        if not volume_data:
            return None

        thresh = vtk.vtkImageThreshold()
        thresh.SetInputData(volume_data)

        if upper_threshold is not None:
            thresh.ThresholdBetween(lower_threshold, upper_threshold)
        else:
            thresh.ThresholdByUpper(lower_threshold)

        thresh.SetInValue(1)
        thresh.SetOutValue(0)
        thresh.Update()

        # Retorna uma cópia profunda para isolar o pipeline do VTK
        output = vtk.vtkImageData()
        output.DeepCopy(thresh.GetOutput())
        return output