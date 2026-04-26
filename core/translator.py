import json
import sys
from pathlib import Path
from gui.settings import settings

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent

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
        language = settings.get("preferencias", "idioma", "pt_BR")
        translation_file = get_base_dir() / "translations" / f"{language}.json"

        try:
            if translation_file.exists():
                cls._dictionary = json.loads(translation_file.read_text(encoding="utf-8"))
            else:
                print(f"Translation error: File not found at {translation_file}")
        except Exception as error:
            print(f"Translation error: {error}")

    def get_text(self, key, default=None):
        try:
            keys = key.split('.')
            result = self._dictionary
            for k in keys:
                result = result[k]
            return result
        except (KeyError, TypeError, AttributeError):
            return default if default is not None else key

_translator_instance = Translator()

def tr(key, default=None):
    return _translator_instance.get_text(key, default)