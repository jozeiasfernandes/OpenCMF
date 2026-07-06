import json
import logging
import sys
from pathlib import Path
from functools import lru_cache
from typing import Any, Optional
from core.home_page.settings_app import settings


def get_base_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent


class Translator:
    _instance: Optional['Translator'] = None
    _dictionary: dict[str, Any] = {}

    def __new__(cls) -> 'Translator':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_dictionary()
        return cls._instance

    def _load_dictionary(self, language: str = None) -> None:
        lang = language or settings.get("preferencias", "idioma", "pt_BR")
        translation_path = (
                get_base_dir() / "core" / "localization" / "translations" / f"{lang}.json"
        )

        if not translation_path.exists():
            logging.error(f"Translation file not found: {translation_path}")
            self._dictionary = {}
            return

        try:
            self._dictionary = json.loads(translation_path.read_text(encoding="utf-8"))
            self.get_text.cache_clear()
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            self._dictionary = {}

    @lru_cache(maxsize=128)
    def get_text(self, key: str, default: Any = None) -> str:
        keys = key.split('.')
        value = self._dictionary

        try:
            for k in keys:
                value = value[k]
            return str(value)
        except (KeyError, TypeError):
            return str(default if default is not None else key)

    def refresh(self, language: str) -> None:
        self._load_dictionary(language)


translator = Translator()


def tr(key: str, default: Any = None) -> str:
    return translator.get_text(key, default)