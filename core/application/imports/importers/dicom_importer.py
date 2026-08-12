from pathlib import Path
from typing import Any, ClassVar, Union

from .base_importer import BaseImporter

from domain.volume import DicomEngine
from domain.volume import DicomValidator


class DicomImporter(BaseImporter):
    """Importador para volumes DICOM."""

    name: ClassVar[str] = "DICOM"

    supported_extensions: ClassVar[tuple[str, ...]] = (
        ".dcm",
    )

    supports_multiple_files: ClassVar[bool] = True

    @staticmethod
    def _target_directory(source: Union[Path, list[Path]]) -> Path:
        """Converte qualquer origem em um diretório DICOM."""
        path = source[0] if isinstance(source, list) else source
        if path.is_dir():
            return path
        return path.parent

    @classmethod
    def supports(cls, source: Union[Path, list[Path]]) -> bool:
        path = source[0] if isinstance(source, list) else source
        return (
                path.is_dir()
                or path.suffix.lower() in cls.supported_extensions
        )

    @classmethod
    def validate(cls, source: Union[Path, list[Path]]) -> bool:
        target = cls._target_directory(source)
        if not target.exists():
            return False

        validator = DicomValidator()
        result = validator.validate_directory(target)
        return result.get("sucesso", False)

    def load(
            self,
            source: Union[Path, list[Path]],
            options: Any = None,
    ) -> Any:
        target = self._target_directory(source)
        engine = DicomEngine()

        volume = engine.load_volume(str(target))

        if volume is None or not volume.is_valid:
            raise RuntimeError(
                f"Não foi possível carregar ou o volume DICOM é inválido:\n{target}"
            )

        return volume

    def create_object(self, volume: Any) -> Any:
        """
        Empacota o volume no formato padrão consumido pelo Scene Manager,
        mantendo a mesma padronização de metadados e transformações.
        """
        return {
            "metadata": {
                "name": getattr(volume, "name", "Exame DICOM"),
                "type": "Volume",
                "mesh_data": volume.vtk_data,  # Compatibilidade com visualizador VTK atual
                "volume_model": volume,  # Modelo completo de volume
                "source_path": str(volume.source_path)
            },
            "transforms": {
                "position": (0.0, 0.0, 0.0),
                "scale": [1.0, 1.0, 1.0]
            }
        }