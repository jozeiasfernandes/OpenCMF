import pytest
from core.windows.translator import Translator


def test_translator_fallback():
    """Garante que chaves inexistentes retornam o próprio nome"""
    translator = Translator()
    # Forçamos um dicionário vazio para teste
    translator._dictionary = {}

    resultado = translator.get_text("chave_inexistente")
    assert resultado == "chave_inexistente"


def test_translator_with_data():
    """Garante que a tradução correta é retornada"""
    translator = Translator()
    translator._dictionary = {"btn_save": "Salvar"}

    assert translator.get_text("btn_save") == "Salvar"