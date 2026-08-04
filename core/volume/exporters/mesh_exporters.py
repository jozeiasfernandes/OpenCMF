import vtk
from pathlib import Path
from typing import Optional, Callable


class MeshExporter:
    """
    Responsável pela persistência e exportação de malhas poligonais (vtkPolyData)
    para formatos de arquivo padrão de mercado (STL, OBJ, PLY).
    """

    @staticmethod
    def salvar_stl(
            polydata: vtk.vtkPolyData,
            caminho_saida: Path,
            binario: bool = True,
            callback_progresso: Optional[Callable[[str, int], None]] = None
    ) -> bool:
        """
        Salva uma malha poligonal em formato STL (Stereolithography).
        """
        if not polydata:
            if callback_progresso:
                callback_progresso("Erro: Dados de malha inválidos para exportação.", -1)
            return False

        try:
            if callback_progresso:
                callback_progresso("Iniciando gravação do arquivo STL...", 50)

            writer = vtk.vtkSTLWriter()
            writer.SetFileName(str(caminho_saida))
            writer.SetInputData(polydata)

            if binario:
                writer.SetFileTypeToBinary()
            else:
                writer.SetFileTypeToASCII()

            writer.Write()

            if callback_progresso:
                callback_progresso("Arquivo STL salvo com sucesso!", 100)
            return True

        except Exception as e:
            if callback_progresso:
                callback_progresso(f"Falha ao exportar STL: {str(e)}", -1)
            return False