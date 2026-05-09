import json
import shutil
import logging
from typing import Dict, Optional
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from .models_import import ObjectProperties

logger = logging.getLogger("ObjectManager")

CATEGORIA_MAPPING = {
    "Superfícies": "surfaces",
    "Fotografias": "photos",
    "Volume": "volume"
}

SUBCATEGORIA_MAPPING = {
    "surfaces": {
        "Crânio": "cranio",
        "Maxila": "maxila",
        "Mandíbula": "mandibula",
        "Pele": "pele",
        "Outros": "outros"
    },
    "photos": {
        "Frente": "frente",
        "Perfil": "perfil",
        "Intrabucal": "intrabucal",
        "Outros": "outros"
    },
    "volume": {
        "Volume .vti": "volume_vti"
    }
}


class ObjectManager(QObject):
    object_added = Signal(ObjectProperties)
    object_removed = Signal(str)

    def __init__(self, patient_path: str) -> None:
        super().__init__()
        self.patient_path = Path(patient_path)
        self.objects: Dict[str, ObjectProperties] = {}
        self.categories = CATEGORIA_MAPPING

        logger.debug(f"ObjectManager inicializado para paciente: {self.patient_path}")

    def import_object(self, file_path: str, category: str, sub_category: str) -> Optional[ObjectProperties]:
        try:
            source = Path(file_path)

            if not source.exists():
                logger.error(f"Arquivo fonte não existe: {file_path}")
                return None

            if not self.patient_path.exists():
                logger.error(f"Caminho do paciente não existe: {self.patient_path}")
                return None

            folder = self.categories.get(category, "others")

            if category not in self.categories:
                logger.warning(f"Categoria não mapeada: '{category}'. Categorias disponíveis: {list(self.categories.keys())}")

            if not self._validar_subcategoria(folder, sub_category):
                logger.warning(f"Subcategoria '{sub_category}' não reconhecida para '{category}'. Usando como está.")

            target_dir = self.patient_path / folder
            target_dir.mkdir(parents=True, exist_ok=True)

            destination = self._get_unique_path(target_dir, source)
            shutil.copy2(source, destination)

            logger.info(f"Arquivo importado: {source.name} -> {destination.relative_to(self.patient_path)}")

            props = ObjectProperties(
                name=destination.stem,
                type=folder,
                file_path=str(destination.relative_to(self.patient_path)),
                format=source.suffix.lower().replace(".", "")
            )

            self._save_object_metadata(destination, props)
            self.objects[props.id] = props
            self.object_added.emit(props)

            logger.debug(f"Objeto adicionado ao gerenciador: {props.id} - {props.name}")

            return props

        except Exception as error:
            logger.error(f"Erro ao importar objeto: {error}", exc_info=True)
            return None

    def _validar_subcategoria(self, folder: str, sub_category: str) -> bool:
        if folder not in SUBCATEGORIA_MAPPING:
            return False

        subcategorias_validas = SUBCATEGORIA_MAPPING[folder]
        return sub_category in subcategorias_validas

    def _get_unique_path(self, target_dir: Path, source: Path) -> Path:
        dest = target_dir / source.name
        counter = 1
        while dest.exists():
            dest = target_dir / f"{source.stem}_{counter}{source.suffix}"
            counter += 1

        logger.debug(f"Caminho único gerado: {dest.name}")
        return dest

    def _save_object_metadata(self, file_path: Path, props: ObjectProperties) -> None:
        try:
            json_path = file_path.with_suffix(".json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(props.to_json(), f, indent=4, ensure_ascii=False)
            logger.debug(f"Metadados salvos: {json_path}")
        except Exception as error:
            logger.error(f"Erro ao salvar metadados: {error}", exc_info=True)

    def load_existing_objects(self) -> None:
        try:
            loaded_count = 0
            for json_file in self.patient_path.rglob("*.json"):
                if "project" in json_file.parts:
                    continue
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        props = ObjectProperties.from_json(data)
                        self.objects[props.id] = props
                        self.object_added.emit(props)
                        loaded_count += 1
                except (json.JSONDecodeError, TypeError, ValueError) as error:
                    logger.warning(f"Erro ao carregar objeto de {json_file}: {error}")
                    continue

            logger.info(f"Objetos carregados: {loaded_count} para paciente {self.patient_path}")
        except Exception as error:
            logger.error(f"Erro ao carregar objetos existentes: {error}", exc_info=True)
