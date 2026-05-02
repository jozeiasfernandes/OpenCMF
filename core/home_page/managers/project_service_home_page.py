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

    def __init__(self, patients_dir: Path):
        self.patients_dir = Path(patients_dir)
        self.patients_dir.mkdir(parents=True, exist_ok=True)

        root_dir = str(self.patients_dir.parent)
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

    def carregar_modulo(self, id_modulo: str) -> Optional[Any]:
        try:
            mapeamento = {
                "Paciente": "patients",
                "modulo.paciente": "patients",
                "mod_patients.paciente": "patients"
            }

            target = mapeamento.get(id_modulo, id_modulo.lower())

            if target.startswith("modules."):
                module_path = target
            else:
                module_path = f"modules.{target}"

            spec = importlib.util.find_spec(module_path)
            if not spec:
                return None

            module_obj = importlib.import_module(module_path)
            classe_modulo = getattr(module_obj, "Modulo", None)

            return classe_modulo() if classe_modulo else None
        except Exception as e:
            logging.error(f"Erro ao carregar {id_modulo}: {e}")
            return None

    def load_project(self, root_path: Path) -> Optional[Dict[str, Any]]:
        return self._read_json(Path(root_path) / self.PROJECT_SUBFOLDER / self.INFO_FILE)

    def save_project(self, root_path: Path, data: Dict[str, Any]):
        folder = Path(root_path) / self.PROJECT_SUBFOLDER
        folder.mkdir(parents=True, exist_ok=True)

        path = folder / self.INFO_FILE
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

    def initialize_patient_structure(self, root_path: Path):
        for sub in [self.PROJECT_SUBFOLDER, "volume", "surfaces", "photos", "others"]:
            (Path(root_path) / sub).mkdir(parents=True, exist_ok=True)

    def list_recent_projects(self) -> List[Dict[str, Any]]:
        projects = []
        pattern = f"*/{self.PROJECT_SUBFOLDER}/{self.INFO_FILE}"

        for info_path in self.patients_dir.glob(pattern):
            data = self._read_json(info_path)
            if data is None: continue

            root = info_path.parents[1]
            data["_path"] = str(root)

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