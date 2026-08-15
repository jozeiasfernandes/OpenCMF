from __future__ import annotations

import copy
import importlib.util
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Paths
from core.settings.paths.list_paths import PATIENTS_DIR


class ProjectServiceHomePage:
    PROJECT_SUBFOLDER = "project_manager"
    INFO_FILE = "info.json"
    DATA_FOLDERS = ["volume", "surfaces", "photos", "others"]

    def __init__(self, patients_dir: Optional[Union[str, Path]] = None):
        self.patients_dir = Path(patients_dir) if patients_dir else PATIENTS_DIR
        self.patients_dir.mkdir(parents=True, exist_ok=True)

        # Nota: Avaliar se a manipulação de sys.path é estritamente necessária aqui
        root_dir = str(self.patients_dir.parent)
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

    def load_project(self, root_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        root = Path(root_path)
        data = None

        for sub in [self.PROJECT_SUBFOLDER, "project", "project_manager"]:
            info_path = root / sub / self.INFO_FILE
            data = self._read_json(info_path)
            if data:
                break

        if data:
            data["_path"] = str(root)
            self._sync_physical_paths(root, data)

        return data

    def _sync_physical_paths(self, root: Path, data: Dict[str, Any]):
        caminhos = data.setdefault("caminhos", {})

        mapping = {
            "volume": "dicom",
            "surfaces": ["maxila", "mandibula", "face"],
            "photos": "fotos"
        }

        for folder in self.DATA_FOLDERS:
            folder_path = root / folder
            if not folder_path.exists():
                continue

            files = list(folder_path.iterdir())
            if not files:
                continue

            target_keys = mapping.get(folder)
            if isinstance(target_keys, list):
                for file in files:
                    for key in target_keys:
                        if key.lower() in file.name.lower():
                            caminhos[key] = str(file)
            elif target_keys:
                caminhos[target_keys] = str(files[0]) if folder != "volume" else str(folder_path)

    def save_project(self, root_path: Union[str, Path], data: Dict[str, Any]):
        root = Path(root_path)
        folder = root / self.PROJECT_SUBFOLDER
        folder.mkdir(parents=True, exist_ok=True)

        # Utiliza deepcopy para evitar mutações indesejadas no objeto original em memória
        clean_data = copy.deepcopy(data)
        clean_data.pop("_path", None)

        path = folder / self.INFO_FILE
        path.write_text(json.dumps(clean_data, indent=4, ensure_ascii=False), encoding="utf-8")

    def initialize_patient_structure(self, root_path: Union[str, Path]):
        root = Path(root_path)
        for sub in [self.PROJECT_SUBFOLDER] + self.DATA_FOLDERS:
            (root / sub).mkdir(parents=True, exist_ok=True)

    def list_recent_projects(self) -> List[Dict[str, Any]]:
        projects = []
        if not self.patients_dir.exists():
            return projects

        for patient_folder in self.patients_dir.iterdir():
            if not patient_folder.is_dir():
                continue

            data = self.load_project(patient_folder)
            if data:
                patient = data.setdefault("paciente", {})
                patient["nome"] = patient.get("nome") or patient_folder.name
                projects.append(data)

        return sorted(projects, key=lambda x: x.get("updated_at", 0), reverse=True)

    def remove_project(self, path: Union[str, Path]) -> bool:
        try:
            target = Path(path)
            if target.is_dir():
                shutil.rmtree(target)
                return True
            return False
        except Exception as e:
            logging.error(f"Erro ao remover o projeto em {path}: {e}")
            return False

    def _read_json(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logging.warning(f"Não foi possível ler o arquivo JSON em {path}: {e}")
        return None

    def get_module_class(self, id_modulo: str) -> Optional[type]:
        try:
            mapeamento = {"Paciente": "new_project", "modulo.paciente": "new_project"}
            target = mapeamento.get(id_modulo, id_modulo.lower())
            path = target if target.startswith("modules.") else f"modules.{target}"

            spec = importlib.util.find_spec(path)
            if not spec:
                return None

            module_obj = importlib.import_module(path)
            return getattr(module_obj, "Module", None)
        except Exception as e:
            logging.error(f"Erro ao importar {id_modulo}: {e}")
            return None