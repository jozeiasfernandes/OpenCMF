from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List


class DicomFile:
    def __init__(
            self,
            path: Path | str,
            instance_number: int,
    ):
        self.path = Path(path) if isinstance(path, str) else path
        self.instance_number = instance_number

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "instance_number": self.instance_number,
        }


class Series:
    def __init__(
            self,
            series_uid: str,
            description: str,
            rows: int,
            columns: int,
            files: List[DicomFile],
    ):
        self.series_uid = series_uid
        self.description = description
        self.rows = rows
        self.columns = columns
        self.files = files

        # Opcional, mas recomendado: Garante que os arquivos estejam ordenados pelo número da instância
        self.sort_files()

    @property
    def slice_count(self) -> int:
        return len(self.files)

    def sort_files(self):
        """Ordena as fatias com base no número da instância."""
        self.files.sort(key=lambda f: f.instance_number)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "series_uid": self.series_uid,
            "description": self.description,
            "rows": self.rows,
            "columns": self.columns,
            "slice_count": self.slice_count,
            "files": [f.to_dict() for f in self.files],
        }