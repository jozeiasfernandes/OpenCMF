import shutil
from pathlib import Path
from typing import Optional
from PySide6 import QtCore

from application.scene.scene_object import SceneObject
from application.scene.utils.factory import SceneObjectFactory
from settings.paths.list_paths import PATIENTS_DIR
from core.settings.logs.logger_manager import scene_logger


class ObjectImporter(QtCore.QObject):
    object_added = QtCore.Signal(object)

    def __init__(self, patient_path: Optional[str] = None) -> None:
        super().__init__()
        if patient_path:
            self.patient_path = Path(patient_path).resolve()
        else:
            self.patient_path = PATIENTS_DIR.resolve()

        scene_logger.debug(f"ObjectImporter inicializado para o diretório: {self.patient_path}")

    def import_external_file(self, file_path: str, category: str) -> Optional[SceneObject]:
        source = Path(file_path)
        if not source.exists():
            scene_logger.error(f"Arquivo de origem não encontrado para importação: {file_path}")
            return None

        try:
            target_dir = self.patient_path / category
            target_dir.mkdir(parents=True, exist_ok=True)
            destination = self._get_unique_path(target_dir, source)

            scene_logger.info(f"Copiando arquivo externo '{source.name}' para a categoria '{category}'...")
            shutil.copy2(source, destination)

            rel_destination = destination.relative_to(self.patient_path)
            scene_obj = SceneObjectFactory.create_from_file(
                file_path=str(rel_destination),
                category=category
            )

            scene_obj.metadata["original_name"] = source.name

            scene_logger.info(f"Objeto de cena criado com sucesso: ID={scene_obj.id}, Categoria={category}")

            self.object_added.emit(scene_obj)
            return scene_obj

        except Exception as e:
            if 'destination' in locals() and destination.exists():
                destination.unlink()
            scene_logger.error(f"Falha crítica na importação do arquivo {file_path}: {e}", exc_info=True)
            return None

    def delete_physical_file(self, rel_path: str) -> None:
        full_path = self.patient_path / rel_path
        try:
            if full_path.exists():
                full_path.unlink()
                scene_logger.info(f"Arquivo físico removido com sucesso: {rel_path}")
        except OSError as e:
            scene_logger.warning(f"Não foi possível remover o arquivo físico {rel_path}: {e}")

    def _get_unique_path(self, target_dir: Path, source: Path) -> Path:
        dest = target_dir / source.name
        counter = 1
        while dest.exists():
            dest = target_dir / f"{source.stem}_{counter}{source.suffix}"
            counter += 1
        return dest