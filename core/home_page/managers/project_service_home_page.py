import json
import logging
import importlib.util
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional


class ProjectServiceHomePage:
    PROJECT_SUBFOLDER = "project"
    INFO_FILE = "info.json"
    DATA_FOLDERS = ["volume", "surfaces", "photos", "others"]

    def __init__(self, patients_dir: Path):
        self.patients_dir = Path(patients_dir)
        self.patients_dir.mkdir(parents=True, exist_ok=True)

        root_dir = str(self.patients_dir.parent)
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

    def load_project(self, root_path: Path) -> Optional[Dict[str, Any]]:
        root = Path(root_path)
        data = self._read_json(root / self.PROJECT_SUBFOLDER / self.INFO_FILE)

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

    def save_project(self, root_path: Path, data: Dict[str, Any]):
        root = Path(root_path)
        folder = root / self.PROJECT_SUBFOLDER
        folder.mkdir(parents=True, exist_ok=True)

        clean_data = data.copy()
        clean_data.pop("_path", None)

        path = folder / self.INFO_FILE
        path.write_text(json.dumps(clean_data, indent=4, ensure_ascii=False), encoding="utf-8")

    def initialize_patient_structure(self, root_path: Path):
        root = Path(root_path)
        for sub in [self.PROJECT_SUBFOLDER] + self.DATA_FOLDERS:
            (root / sub).mkdir(parents=True, exist_ok=True)

    def list_recent_projects(self) -> List[Dict[str, Any]]:
        projects = []
        pattern = f"*/{self.PROJECT_SUBFOLDER}/{self.INFO_FILE}"

        for info_path in self.patients_dir.glob(pattern):
            root = info_path.parents[1]
            data = self.load_project(root)
            if data:
                patient = data.setdefault("paciente", {})
                patient["nome"] = patient.get("nome") or root.name
                projects.append(data)

        return sorted(projects, key=lambda x: x.get("updated_at", 0), reverse=True)

    def remove_project(self, path: str) -> bool:
        try:
            target = Path(path)
            if target.is_dir():
                shutil.rmtree(target)
                return True
            return False
        except Exception:
            return False

    def _read_json(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return None

    def carregar_modulo(self, id_modulo: str) -> Optional[Any]:
        try:
            mapeamento = {"Paciente": "patients", "modulo.paciente": "patients"}
            target = mapeamento.get(id_modulo, id_modulo.lower())
            module_path = target if target.startswith("modules.") else f"modules.{target}"

            spec = importlib.util.find_spec(module_path)
            if not spec: return None

            module_obj = importlib.import_module(module_path)
            classe = getattr(module_obj, "Modulo", None)
            return classe() if classe else None
        except Exception as e:
            logging.error(f"Erro modulo {id_modulo}: {e}")
            return None