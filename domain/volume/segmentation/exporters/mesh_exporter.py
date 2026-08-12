import vtk
from pathlib import Path
from typing import Optional, Callable


class MeshExporter:
    """
    Responsável pela persistência e exportação de malhas geométricas (vtkPolyData)
    para formatos de arquivo padrão, como STL.
    """

    @staticmethod
    def salvar_stl(
        polydata: vtk.vtkPolyData,
        caminho_saida: Path,
        binario: bool = True,
        callback_progresso: Optional[Callable[[str, int], None]] = None
    ) -> bool:
        """
        Salva um objeto vtkPolyData em um arquivo STL (binário ou ASCII).
        """
        if not polydata or polydata.GetNumberOfCells() == 0:
            if callback_progresso:
                callback_progresso("Erro: Malha geométrica vazia ou inválida.", -1)
            return False

        try:
            # Garante que o diretório de destino exista
            caminho_saida = Path(caminho_saida)
            caminho_saida.parent.mkdir(parents=True, exist_ok=True)

            if callback_progresso:
                callback_progresso("Iniciando exportação do arquivo STL...", 10)

            writer = vtk.vtkSTLWriter()
            writer.SetFileName(str(caminho_saida))
            writer.SetInputData(polydata)

            if binario:
                writer.SetFileTypeToBinary()
            else:
                writer.SetFileTypeToASCII()

            if callback_progresso:
                callback_progresso("Gravando dados no disco...", 50)

            writer.Write()

            if callback_progresso:
                callback_progresso("Exportação concluída com sucesso.", 100)

            return True

        except Exception as e:
            if callback_progresso:
                callback_progresso(f"Erro ao salvar arquivo STL: {str(e)}", -1)
            return False