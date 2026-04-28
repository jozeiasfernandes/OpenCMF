import json
import sys
import logging
from pathlib import Path
from appearance.settings import settings


def get_base_dir():
    """Retorna a raiz do projeto (OpenCMF)."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    # Como este arquivo está em core/localization, .parent.parent volta para a raiz
    return Path(__file__).resolve().parent.parent.parent


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
        # Busca o idioma configurado ou assume pt_BR como padrão
        language = settings.get("preferencias", "idioma", "pt_BR")

        # CAMINHO ATUALIZADO: reflete a nova estrutura core/localization/translations
        translation_file = get_base_dir() / "core" / "localization" / "translations" / f"{language}.json"

        try:
            if translation_file.exists():
                cls._dictionary = json.loads(translation_file.read_text(encoding="utf-8"))
            else:
                logging.error(f"Translation error: File not found at {translation_file}")
                # Fallback vazio para não quebrar o código
                cls._dictionary = {}
        except Exception as error:
            logging.error(f"Translation error during initialization: {error}")
            cls._dictionary = {}

    def get_text(self, key, default=None):
        """Busca a tradução pela chave (ex: 'menu.file.open')."""
        try:
            keys = key.split('.')
            result = self._dictionary
            for k in keys:
                result = result[k]
            return result
        except (KeyError, TypeError, AttributeError):
            # Se não achar a tradução, retorna o default ou a própria chave
            return default if default is not None else key


# Instância Singleton
_translator_instance = Translator()


def tr(key, default=None):
    """Função global para tradução rápida."""
    return _translator_instance.get_text(key, default)