import sys
from pathlib import Path


def get_project_root() -> Path:
    """Retorna a raiz do projeto de forma dinâmica (compatível com PyInstaller/frozen)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


# Diretórios do sistema
BASE_DIR = get_project_root()

# Configurações do sistema
APPEARANCE_DIR = BASE_DIR / "appearance"
ICONS_DIR = APPEARANCE_DIR / "icons"
ICONS_THEMES_DIR = APPEARANCE_DIR / "icons_themes"
THEMES_DIR = APPEARANCE_DIR / "themes"
CONFIG_FILE_PATH = BASE_DIR / "config.json"
TRANSLATIONS_DIR = BASE_DIR / "core" / "settings" / "localization" / "translations"
SHORTCUTS_FILE_PATH = BASE_DIR / "core" / "settings" / "shortcuts" / "shortcuts.json"

# Diretórios do paciente
PATIENTS_DIR = BASE_DIR / "patients"
FLOWS_DIR = BASE_DIR / "flows"
DEFAULT_FLOW_PATH = FLOWS_DIR / "default_flow.json"
REGISTRATION_FLOW_NAME = "new_patient_registration.json"
REGISTRATION_FLOW_PATH = FLOWS_DIR / REGISTRATION_FLOW_NAME

# Volume
PRESETS_DIR = BASE_DIR / "core" / "volume" / "visualization" / "presets"