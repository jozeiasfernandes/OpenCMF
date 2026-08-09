from __future__ import annotations

import json
import os
from typing import Dict, Optional
from PySide6.QtCore import QDir, QStandardPaths

# Settings
from core.settings.localization.translator import tr
from core.settings.paths.list_paths import FAVORITE_FOLDERS_FILE


class FileBrowserController:
    """
    Controlador responsável pela lógica de negócios do explorador de arquivos,
    incluindo favoritos persistidos em JSON e manipulação de diretórios.
    """

    @staticmethod
    def get_system_shortcuts() -> dict[str, str]:
        """Retorna os atalhos padrão do sistema operacional com nomes traduzíveis."""
        shortcuts: dict[str, str] = {}

        # Mapeamento de nomes para chaves de tradução
        locations = [
            ("file_browser.home", QStandardPaths.StandardLocation.HomeLocation),
            ("file_browser.documents", QStandardPaths.StandardLocation.DocumentsLocation),
            ("file_browser.downloads", QStandardPaths.StandardLocation.DownloadLocation),
            ("file_browser.pictures", QStandardPaths.StandardLocation.PicturesLocation),
            ("file_browser.desktop", QStandardPaths.StandardLocation.DesktopLocation),
            ("file_browser.music", QStandardPaths.StandardLocation.MusicLocation),
            ("file_browser.movies", QStandardPaths.StandardLocation.MoviesLocation),
        ]

        for key, loc_type in locations:
            paths = QStandardPaths.standardLocations(loc_type)
            if paths:
                path = paths[0]
                if QDir(path).exists():
                    # Traduz o nome da pasta usando a chave correspondente
                    display_name = tr(key, key.split('.')[-1].capitalize())
                    shortcuts[display_name] = path

        # Tradução do atalho raiz
        root_name = tr("file_browser.root", "Raiz (/)")
        shortcuts[root_name] = QDir.rootPath()

        return shortcuts

    @classmethod
    def load_favorites(cls) -> Dict[str, str]:
        """Carrega as pastas favoritas do arquivo JSON centralizado."""
        fav_path = str(FAVORITE_FOLDERS_FILE)
        if not os.path.exists(fav_path):
            return {}
        try:
            with open(fav_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    @classmethod
    def save_favorites(cls, favorites: Dict[str, str]) -> None:
        """Salva o dicionário de favoritos no arquivo JSON centralizado."""
        try:
            fav_path = str(FAVORITE_FOLDERS_FILE)
            os.makedirs(os.path.dirname(fav_path), exist_ok=True)
            with open(fav_path, "w", encoding="utf-8") as f:
                json.dump(favorites, f, indent=4, ensure_ascii=False)
        except Exception as e:
            # Em um cenário real, considere logar esse erro via logging
            print(f"Erro ao salvar favoritos: {e}")

    @staticmethod
    def create_new_directory(current_path: str, folder_name: str) -> Optional[str]:
        """Cria uma nova subpasta no diretório atual."""
        if not current_path or not folder_name:
            return None
        new_dir_path = os.path.join(current_path, folder_name)
        try:
            os.makedirs(new_dir_path, exist_ok=True)
            return new_dir_path
        except Exception as e:
            print(f"Erro ao criar pasta: {e}")
            return None

    @staticmethod
    def clean_path(path: str) -> str:
        return QDir.cleanPath(path)

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        if size_bytes >= 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        if size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        if size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        return f"{size_bytes} {tr('file_browser.bytes', 'bytes')}"