import shutil
import logging
import uuid
from typing import Optional, List
from pathlib import Path
from PySide6.QtCore import QObject, Signal

from core.scene.scene_object import SceneObject
from core.scene.persistence.serializer import Serializer
from core.scene.events.scene_events import OBJECT_ADDED
from core.scene.utils.scene_utils import SceneUtils

logger = logging.getLogger("OpenCMF.ObjectManager")


class ObjectManager(QObject):
    object_added = Signal(SceneObject)
    object_removed = Signal(str)

    def __init__(self, patient_path: str, serializer: Serializer, event_bus=None) -> None:
        super().__init__()
        self.patient_path = Path(patient_path)
        self.serializer = serializer
        self.event_bus = event_bus
        self.project_file = self.patient_path / "project" / "scene.cmf"

        self.project_file.parent.mkdir(parents=True, exist_ok=True)
        self._current_objects: List[SceneObject] = []

    def import_external_file(self, file_path: str, category: str, obj_id: Optional[str] = None) -> Optional[
        SceneObject]:
        source = Path(file_path)
        if not source.exists():
            return None

        try:
            target_dir = self.patient_path / category
            target_dir.mkdir(parents=True, exist_ok=True)

            destination = self._get_unique_path(target_dir, source)
            shutil.copy2(source, destination)

            scene_obj = SceneUtils.create_from_file(
                obj_id=obj_id or str(uuid.uuid4())[:12],
                name=destination.stem,
                category=category,
                rel_path=str(destination.relative_to(self.patient_path))
            )

            self._current_objects.append(scene_obj)
            self.save_scene(self._current_objects)

            if self.event_bus:
                self.event_bus.emit(OBJECT_ADDED, object=scene_obj)
            self.object_added.emit(scene_obj)

            return scene_obj

        except Exception as e:
            logger.error(f"Erro na importação: {e}", exc_info=True)
            return None

    def save_scene(self, objects: List[SceneObject]) -> None:
        try:
            self._current_objects = objects
            json_string = self.serializer.save(objects)
            self.project_file.write_text(json_string, encoding="utf-8")
        except Exception as e:
            logger.error(f"Erro ao salvar cena .cmf: {e}")

    def load_patient_data(self) -> None:
        if not self.project_file.exists():
            return

        try:
            raw_data = self.project_file.read_text(encoding="utf-8")
            self._current_objects = self.serializer.load(raw_data)

            for obj in self._current_objects:
                if self.event_bus:
                    self.event_bus.emit(OBJECT_ADDED, object=obj)
                self.object_added.emit(obj)
        except Exception as e:
            logger.error(f"Erro ao carregar projeto .cmf: {e}")

    def remove_object(self, object_id: str) -> None:
        obj_to_remove = next((o for o in self._current_objects if o.id == object_id), None)

        if obj_to_remove:
            self._delete_physical_file(obj_to_remove.file_path)
            self._current_objects = [o for o in self._current_objects if o.id != object_id]
            self.save_scene(self._current_objects)
            self.object_removed.emit(object_id)

    def _get_unique_path(self, target_dir: Path, source: Path) -> Path:
        dest = target_dir / source.name
        counter = 1
        while dest.exists():
            dest = target_dir / f"{source.stem}_{counter}{source.suffix}"
            counter += 1
        return dest

    def _delete_physical_file(self, rel_path: str) -> None:
        full_path = self.patient_path / rel_path
        try:
            if full_path.exists():
                full_path.unlink()
        except Exception as e:
            logger.warning(f"Erro ao deletar arquivo físico: {e}")