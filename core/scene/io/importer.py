import shutil
import logging
from pathlib import Path
from typing import Optional
from PySide6 import QtCore

from core.scene.scene_object import SceneObject
from core.scene.utils.factory import SceneObjectFactory

logger = logging.getLogger(__name__)


class ObjectImporter(QtCore.QObject):

    object_added = QtCore.Signal(object)

    def __init__(self, patient_path: str) -> None:
        super().__init__()  # CRÍTICO: Inicializa o QObject corretamente
        self.patient_path = Path(patient_path)

    def import_external_file(self, file_path: str, category: str) -> Optional[SceneObject]:
        source = Path(file_path)
        if not source.exists():
            logger.error(f"Arquivo de origem não encontrado: {file_path}")
            return None

        try:
            target_dir = self.patient_path / category
            target_dir.mkdir(parents=True, exist_ok=True)
            destination = self._get_unique_path(target_dir, source)

            shutil.copy2(source, destination)

            # Uso consistente da Factory
            scene_obj = SceneObjectFactory.create_from_file(
                file_path=str(destination.relative_to(self.patient_path)),
                category=category
            )

            scene_obj.metadata["original_name"] = source.name

            # Emite o sinal para que os observadores (Modulo/Registry) recebam o objeto
            self.object_added.emit(scene_obj)

            return scene_obj

        except Exception as e:
            if 'destination' in locals() and destination.exists():
                destination.unlink()
            logger.error(f"Falha na importação de {file_path}: {e}", exc_info=True)
            return None

    def delete_physical_file(self, rel_path: str) -> None:
        full_path = self.patient_path / rel_path
        try:
            if full_path.exists():
                full_path.unlink()
        except OSError as e:
            logger.warning(f"Não foi possível remover o arquivo {rel_path}: {e}")

    def _get_unique_path(self, target_dir: Path, source: Path) -> Path:
        dest = target_dir / source.name
        counter = 1
        while dest.exists():
            dest = target_dir / f"{source.stem}_{counter}{source.suffix}"
            counter += 1
        return dest