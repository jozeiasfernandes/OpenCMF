from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Localization
from core.settings.localization.translator import tr

# Paths
from core.settings.paths.list_paths import PATIENTS_DIR


class PatientConfigManager:
    PROJECT_SUBFOLDER = "project"
    RECORD_FILE = "patient_record.json"

    def __init__(self) -> None:
        super().__init__()

    def load_patient_record(self, root_path: Union[str, Path, None] = None) -> Optional[Dict[str, Any]]:
        logging.debug(f"[DEBUG] Tentando carregar de: {root_path}")

        if not root_path:
            logging.warning("[DEBUG] root_path fornecido ao load_patient_record é NULO ou VAZIO!")
            return None

        root = Path(root_path)
        record_path = root / self.PROJECT_SUBFOLDER / self.RECORD_FILE

        logging.debug(f"[DEBUG] Caminho final montado: {record_path}")
        logging.debug(f"[DEBUG] O arquivo existe? {record_path.exists()}")

        try:
            if record_path.exists():
                return json.loads(record_path.read_text(encoding="utf-8"))
        except Exception as e:
            logging.error(f"Erro ao ler o registro em {record_path}: {e}")
        return None

    def save_patient_record(self, root_path: Union[str, Path, None] = None, data: Dict[str, Any] = None) -> bool:
        root = Path(root_path) if root_path else PATIENTS_DIR
        record_path = root / self.PROJECT_SUBFOLDER / self.RECORD_FILE
        data = data if data is not None else {}

        try:
            record_path.parent.mkdir(parents=True, exist_ok=True)

            with open(record_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            logging.info(
                tr(
                    "patient.save_config_success",
                    f"Registro do paciente salvo com sucesso em: {record_path}",
                )
            )
            return True
        except Exception as e:
            logging.error(
                tr(
                    "patient.save_config_error",
                    f"Erro ao salvar o registro do paciente em {record_path}: {e}",
                )
            )
            return False

    def update_record_field(self, root_path: Union[str, Path, None], key: str, value: Any) -> bool:
        data = self.load_patient_record(root_path)
        if data is None:
            data = {}

        data[key] = value
        return self.save_patient_record(root_path, data)