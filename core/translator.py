import json
import sys
from pathlib import Path
from gui.settings import settings


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent


class Translator:
    _instance = None
    _dictionary = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls.initialize()
        return cls._instance

    @classmethod
    def initialize(cls):
        lang = settings.get("preferencias", "idioma", "pt_BR")
        file_path = get_base_dir() / "translations" / f"{lang}.json"

        try:
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                cls._dictionary = json.loads(content)
            else:
                print(f"Warning: Translation file not found at {file_path}")
        except Exception as error:
            print(f"Error loading translation: {error}")

    def get_text(self, key, default=None):
        fallback = default if default else key
        return self._dictionary.get(key, fallback)


tr = Translator().get_text