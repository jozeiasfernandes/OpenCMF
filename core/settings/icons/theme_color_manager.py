from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from core.settings.paths.list_paths import THEMES_DIR

logger = logging.getLogger(f"OpenCMF.Core.{__name__.split('.')[-1]}")


class ThemeColorManager:
    """Gerenciador responsável por carregar e extrair cores diretamente dos arquivos .qss dos temas."""

    _instance: Optional[ThemeColorManager] = None

    def __init__(self) -> None:
        self._themes_cache: dict[str, str] = {}

    @classmethod
    def get_instance(cls) -> ThemeColorManager:
        if cls._instance is None:
            cls._instance = ThemeColorManager()
        return cls._instance

    def clear_cache(self) -> None:
        self._themes_cache.clear()

    def get_color(self, theme_name: str, group: str, state: str = "default") -> str:
        """Lê o arquivo .qss do tema e deduz a cor ideal com base nas regras de estilo."""
        if not theme_name:
            return "#FFFFFF"

        qss_content = self._load_theme_qss(theme_name)
        if not qss_content:
            return "#FFFFFF"

        # Se for um estado de hover ou primário, podemos procurar cores de destaque comuns no QSS (ex: #3498DB)
        if state == "hover" or group == "primary":
            match_accent = re.search(r"background-color:\s*(#[0-9a-fA-F]{6});", qss_content)
            if match_accent:
                return match_accent.group(1)

        # Caso padrão: tenta extrair a cor principal de texto (color:) do QWidget no QSS
        match_color = re.search(r"QWidget\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6});", qss_content, re.DOTALL)
        if match_color:
            return match_color.group(1)

        # Fallback universal se não achar nada específico
        return "#333333" if "claro" in theme_name.lower() else "#FFFFFF"

    def _load_theme_qss(self, theme_name: str) -> str:
        """Carrega o conteúdo do arquivo .qss e armazena em cache."""
        if theme_name in self._themes_cache:
            return self._themes_cache[theme_name]

        # Ajuste para procurar o arquivo .qss na pasta de temas
        qss_path = THEMES_DIR / f"{theme_name}.qss"
        content = ""

        try:
            if qss_path.exists():
                with open(qss_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                logger.warning(f"Arquivo QSS de tema não encontrado: {qss_path}")
        except IOError as e:
            logger.error(f"Erro ao ler arquivo QSS '{theme_name}' em {qss_path}: {e}")

        self._themes_cache[theme_name] = content
        return content