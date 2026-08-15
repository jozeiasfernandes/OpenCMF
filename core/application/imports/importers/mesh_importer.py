from pathlib import Path
from typing import Any, List, Union

from .base_importer import BaseImporter
from vtkmodules.vtkIOGeometry import vtkSTLReader


class MeshImporter(BaseImporter):
    """Importador para modelos tridimensionais (STL, OBJ, PLY) utilizando VTK."""

    name: str = "Malha 3D"

    supported_extensions: tuple[str, ...] = (
        ".stl",
        ".obj",
        ".ply",
    )

    supports_multiple_files: bool = True

    @classmethod
    def validate(cls, source: Union[Path, List[Path]]) -> bool:
        primary_path = source[0] if isinstance(source, list) else source
        if primary_path.is_dir() or not cls.supports(primary_path):
            return False

        paths = source if isinstance(source, list) else [source]

        return all(
            path.exists() and path.is_file() and path.suffix.lower() in cls.supported_extensions
            for path in paths
        )

    def load(self, source: Union[Path, List[Path]], options: Any = None) -> Any:
        is_list = isinstance(source, list)
        paths = source if is_list else [source]

        meshes = []

        for path in paths:
            ext = path.suffix.lower()
            if ext == ".stl":
                reader = vtkSTLReader()
                reader.SetFileName(str(path))
                reader.Update()

                # Armazena o vtkPolyData diretamente junto com o path de origem
                meshes.append({
                    "path": path,
                    "poly_data": reader.GetOutput()
                })

            # OBJ e PLY futuramente...

        if not meshes:
            raise ValueError("Nenhuma malha válida foi carregada.")

        return meshes if is_list and len(meshes) > 1 else meshes[0]

    def create_object(self, data: Any) -> Any:
        """
        Nesta etapa sem classes personalizadas, o objeto criado
        é o próprio dicionário estruturado ou o vtkPolyData bruto,
        pronto para ser consumido pelo gerenciador de cena.
        """
        return data