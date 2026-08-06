from pathlib import Path


class DicomFile:
    def __init__(
        self,
        path: Path,
        instance_number: int,
    ):
        self.path = path
        self.instance_number = instance_number

    def to_dict(self):
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
        files: list[DicomFile],
    ):
        self.series_uid = series_uid
        self.description = description
        self.rows = rows
        self.columns = columns
        self.files = files

    @property
    def slice_count(self):
        return len(self.files)

    def to_dict(self):
        return {
            "series_uid": self.series_uid,
            "description": self.description,
            "rows": self.rows,
            "columns": self.columns,
            "slice_count": self.slice_count,
            "files": [f.to_dict() for f in self.files],
        }