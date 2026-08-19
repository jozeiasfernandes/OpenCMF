from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Union

# Localization
from core.settings.localization.translator import tr

# Paths
from core.settings.paths.list_paths import PATIENTS_DIR


class PatientFolderManager:
    PROJECT_SUBFOLDER = "project"
    DATA_FOLDERS = ["volume", "surfaces", "photos", "others"]

    def __init__(self) -> None:
        super().__init__()

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    def create_patient_structure(self, root_path: Union[str, Path, None] = None) -> Path:
        """Cria a estrutura física do paciente. Se nenhum caminho for fornecido, utiliza PATIENTS_DIR por padrão."""
        root = Path(root_path) if root_path else PATIENTS_DIR

        (root / self.PROJECT_SUBFOLDER).mkdir(parents=True, exist_ok=True)

        for sub in self.DATA_FOLDERS:
            (root / sub).mkdir(parents=True, exist_ok=True)

        logging.info(
            tr(
                "patient.folder_created_log",
                f"Estrutura física do paciente criada/verificada com sucesso em: {root}",
            )
        )
        return root

    def patient_folder_exists(self, root_path: Union[str, Path]) -> bool:
        root = Path(root_path)
        project_manager_path = root / self.PROJECT_SUBFOLDER
        return root.is_dir() and project_manager_path.is_dir()

    def remove_patient_folder(self, root_path: Union[str, Path]) -> bool:
        try:
            target = Path(root_path)
            if target.is_dir():
                shutil.rmtree(target)
                logging.info(
                    tr(
                        "patient.folder_removed_log",
                        f"Pasta física do paciente removida com sucesso: {target}",
                    )
                )
                return True
            return False
        except Exception as e:
            logging.error(
                tr(
                    "patient.folder_remove_error_log",
                    f"Erro ao remover a pasta física do paciente em {root_path}: {e}",
                )
            )
            return False