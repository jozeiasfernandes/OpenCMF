from pathlib import Path
import logging
import vtk

logger = logging.getLogger(__name__)


class VtiExporter:
    @staticmethod
    def save_to_vti(vtk_data: vtk.vtkImageData, output_path: str | Path) -> bool:
        """Salva um objeto vtkImageData em formato .vti no disco."""
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            writer = vtk.vtkXMLImageDataWriter()
            writer.SetFileName(str(path))
            writer.SetInputData(vtk_data)

            result = writer.Write()
            if result == 1:
                logger.info(f"Volume VTI gerado com sucesso em: {path}")
                return True
            else:
                logger.error(f"Falha ao escrever o arquivo VTI em: {path}")
                return False

        except Exception as e:
            logger.error(f"Erro inesperado ao salvar arquivo VTI: {e}")
            return False