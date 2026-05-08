import json
import shutil
from typing import Dict, Optional
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from .models_import import ObjectProperties



class ObjectManager(QObject):
    object_added = Signal(ObjectProperties)
    object_removed = Signal(str)

    def __init__(self, patient_path: str):
        super().__init__()
        self.patient_path = Path(patient_path)
        self.objects: Dict[str, ObjectProperties] = {}

        self.categories = {
            "Superfícies": "surfaces",
            "Fotografias": "photos",
            "Volume": "volume"
        }

    def import_object(self, file_path: str, category: str, sub_category: str) -> Optional[ObjectProperties]:
        source = Path(file_path)
        folder = self.categories.get(category, "others")
        target_dir = self.patient_path / folder
        target_dir.mkdir(parents=True, exist_ok=True)

        destination = self._get_unique_path(target_dir, source)
        shutil.copy2(source, destination)

        props = ObjectProperties(
            name=sub_category,
            type=folder,
            file_path=str(destination.relative_to(self.patient_path)),
            format=source.suffix.lower().replace(".", "")
        )

        self._save_object_metadata(destination, props)
        self.objects[props.id] = props
        self.object_added.emit(props)

        return props

    def _get_unique_path(self, target_dir: Path, source: Path) -> Path:
        dest = target_dir / source.name
        counter = 1
        while dest.exists():
            dest = target_dir / f"{source.stem}_{counter}{source.suffix}"
            counter += 1
        return dest

    def _save_object_metadata(self, file_path: Path, props: ObjectProperties):
        json_path = file_path.with_suffix(".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(props.to_json(), f, indent=4, ensure_ascii=False)

    def load_existing_objects(self):
        for json_file in self.patient_path.rglob("*.json"):
            if "project" in json_file.parts:
                continue
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    props = ObjectProperties.from_json(data)
                    self.objects[props.id] = props
                    self.object_added.emit(props)
            except Exception:
                continue