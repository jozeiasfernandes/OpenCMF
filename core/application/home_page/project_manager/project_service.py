from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Paths
from core.settings.paths.list_paths import PATIENTS_DIR


class ProjectServiceHomePage:
    PROJECT_SUBFOLDER = "project"
    RECORD_FILE = "patient_record.json"

    def __init__(self, patients_dir: Optional[Union[str, Path]] = None):
        self.patients_dir = Path(patients_dir) if patients_dir else PATIENTS_DIR
        self.patients_dir.mkdir(parents=True, exist_ok=True)

    def list_recent_projects(self) -> List[Dict[str, Any]]:
        """Lista os projetos existentes na pasta de pacientes apenas para exibição na vitrine."""
        projects = []
        if not self.patients_dir.exists():
            return projects

        for patient_folder in self.patients_dir.iterdir():
            if not patient_folder.is_dir():
                continue

            record_path = patient_folder / self.PROJECT_SUBFOLDER / self.RECORD_FILE
            data = self._read_json(record_path)

            if data:
                # Injeta o caminho físico para uso da UI ao selecionar o card/item
                data["_path"] = str(patient_folder)

                # Correção: Padronizado para 'paciente' (com 'c') para alinhar com a UI
                patient = data.setdefault("paciente", {})
                patient["nome"] = patient.get("nome") or patient.get("name") or patient_folder.name

                projects.append(data)

        return sorted(projects, key=lambda x: x.get("updated_at", 0), reverse=True)

    def remove_project(self, path: Union[str, Path]) -> bool:
        """Remove a pasta física do projeto/paciente do disco."""
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
            logging.warning(f"Não foi possível ler o arquivo de registro em {path}: {e}")
        return None