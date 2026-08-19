from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Union

# Localization
from core.settings.localization.translator import tr


class PatientPathsManager:
    """Responsável por resolver caminhos absolutos e explorar arquivos nas pastas físicas do paciente."""

    DATA_FOLDERS = ["volume", "surfaces", "photos", "others"]

    def __init__(self) -> None:
        super().__init__()

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    def get_absolute_path(self, root_path: Union[str, Path], relative_path: Union[str, Path]) -> Optional[Path]:
        """Converte um caminho relativo ou lógico em um caminho absoluto validado no disco."""
        if not root_path or not relative_path:
            return None

        root = Path(root_path)
        target = Path(relative_path)

        # Se já for absoluto e existir, retorna
        if target.is_absolute() and target.exists():
            return target

        # Resolve em relação à pasta raiz do paciente
        resolved = root / target
        if resolved.exists():
            return resolved

        return None

    def list_folder_files(self, root_path: Union[str, Path], folder_name: str) -> List[Path]:
        """Lista todos os arquivos presentes em uma subpasta específica do paciente (ex: 'volume', 'surfaces')."""
        root = Path(root_path)
        folder_path = root / folder_name

        if not folder_path.is_dir():
            return []

        try:
            return [file for file in folder_path.iterdir() if file.is_file()]
        except Exception as e:
            logging.error(
                tr(
                    "patient.list_folder_error",
                    f"Erro ao listar arquivos da pasta {folder_name} em {root_path}: {e}",
                )
            )
            return []

    def find_files_by_keyword(self, root_path: Union[str, Path], folder_name: str, keyword: str) -> List[Path]:
        """Busca arquivos dentro de uma pasta específica do paciente que contenham uma palavra-chave no nome."""
        files = self.list_folder_files(root_path, folder_name)
        keyword_lower = keyword.lower()

        return [f for f in files if keyword_lower in f.name.lower()]