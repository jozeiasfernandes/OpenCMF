'''
Responsabilidades:
* Gerenciar caminhos de arquivos (criação de diretórios, nomes únicos).
* Realizar a cópia física de arquivos externos para o diretório do paciente.
* Remover arquivos físicos da cena quando solicitado.
* Fornecer caminhos relativos ao SceneManager.

'''
import shutil
import logging
from pathlib import Path
from typing import Optional

from core.scene.scene_object import SceneObject
# Substituímos SceneUtils pela nova Factory
from core.scene.utils.factory import SceneObjectFactory

logger = logging.getLogger("OpenCMF.ObjectImporter")

import shutil
import logging
from pathlib import Path
from typing import Optional
from core.scene.utils.factory import SceneObjectFactory
from core.scene.scene_object import SceneObject

logger = logging.getLogger(__name__)


class ObjectImporter:
    def __init__(self, patient_path: str) -> None:
        self.patient_path = Path(patient_path)

    def import_external_file(self, file_path: str, category: str) -> Optional[SceneObject]:
        source = Path(file_path)
        if not source.exists():
            logger.error(f"Arquivo de origem não encontrado: {file_path}")
            return None

        try:
            # 1. Preparação do destino
            target_dir = self.patient_path / category
            target_dir.mkdir(parents=True, exist_ok=True)
            destination = self._get_unique_path(target_dir, source)

            # 2. Cópia física
            shutil.copy2(source, destination)

            # 3. Criação via Factory (Alinhada com a assinatura create_from_file)
            # Nota: Passamos file_path (absoluto ou relativo ao patient_path)
            # e a categoria para definir o tipo.
            scene_obj = SceneObjectFactory.create_from_file(
                file_path=str(destination),
                type=category
            )

            # Adicional: Podemos injetar metadados extras se necessário
            scene_obj.metadata["original_name"] = source.name

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