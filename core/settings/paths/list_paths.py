from __future__ import annotations

import sys
from pathlib import Path

def get_project_root() -> Path:
    """
    Retorna a raiz do projeto.

    Compatível com execução normal e PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent.parent.parent.parent


BASE_DIR = get_project_root()


# ==============================================================================
# RUNTIME
# ==============================================================================

LOGS_DIR = BASE_DIR / "logs"

CACHE_DIR = BASE_DIR / "cache"

TEMP_DIR = BASE_DIR / "temp"

PATIENTS_DIR = BASE_DIR / "patients"


# ==============================================================================
# UTILITIES
# ==============================================================================

def resource(*parts: str) -> Path:
    """
    Retorna um path relativo à raiz do projeto.

    Exemplo:
        resource("core", "settings", "icons_manager", "icons_manager", "save.svg")
    """
    return BASE_DIR.joinpath(*parts)


def ensure_runtime_directories() -> None:
    """
    Cria apenas diretórios utilizados em tempo de execução.
    """
    for directory in (
        PATIENTS_DIR,
        LOGS_DIR,
        CACHE_DIR,
        TEMP_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# SETTINGS
# ==============================================================================

CORE_DIR = BASE_DIR / "core"


# Settings
SETTINGS_DIR = BASE_DIR / "core" / "settings"

CONFIG_FILE = SETTINGS_DIR / "config.json"

CONFIG_FILE_PATH = CONFIG_FILE

SETTINGS_PAGE_TABS_DIR = SETTINGS_DIR / "settings_page_tabs"


APPLICATION_DIR = CORE_DIR / "application"

FAVORITE_FOLDERS_FILE = BASE_DIR / "core" / "application" / "file_browser" / "favorite_folders.json"


# Localization
SETTINGS_LOCALIZATION_DIR = SETTINGS_DIR / "localization" / "translations"

TRANSLATIONS_DIR = SETTINGS_DIR / "localization" / "translations"

# Shortcuts
SETTINGS_SHORTCUTS_DIR = SETTINGS_DIR / "shortcuts"

SHORTCUTS_FILE = SETTINGS_DIR / "shortcuts" / "shortcuts.json"

SHORTCUTS_FILE_PATH = SHORTCUTS_FILE

# Help
SETTINGS_HELP_DIR = SETTINGS_DIR / "help"


# Logs
SETTINGS_LOGS_DIR = SETTINGS_DIR / "logs"

SETTINGS_LOGS_ARCHIVES_DIR = SETTINGS_LOGS_DIR / "archives"



# ==============================================================================
# FLOWS
# ==============================================================================

FLOWS_DIR = BASE_DIR / "core" / "application" / "flows" / "list_flows"

DEFAULT_FLOW_FILE = FLOWS_DIR / "default_flow.json"

REGISTRATION_FLOW_FILE = FLOWS_DIR / "new_patient_registration.json"

REGISTRATION_FLOW_NAME = REGISTRATION_FLOW_FILE.name


# ==============================================================================
# APPEARANCE
# ==============================================================================

APPEARANCE_DIR = SETTINGS_DIR

SETTINGS_ICONS_DIR = SETTINGS_DIR / "icons_manager"

ICONS_DIR = SETTINGS_DIR / "icons_manager" / "icons"

SETTINGS_THEMES_DIR = SETTINGS_DIR / "themes_manager"

THEMES_DIR = SETTINGS_DIR / "themes_manager" / "themes"



# ==============================================================================
# SCENE
# ==============================================================================

SCENE_DIR = CORE_DIR / "scene"

SCENE_EVENTS_DIR = SCENE_DIR / "events"

SCENE_IO_DIR = SCENE_DIR / "io"

SCENE_PERSISTENCE_DIR = SCENE_DIR / "persistence"

SCENE_REGISTRY_DIR = SCENE_DIR / "registry"

SCENE_RENDERING_DIR = SCENE_DIR / "rendering"

SCENE_SELECTION_DIR = SCENE_DIR / "selection"

SCENE_UTILS_DIR = SCENE_DIR / "utils"


# ==============================================================================
# WORKSPACE
# ==============================================================================

WORKSPACE_DIR = CORE_DIR / "workspace"

WORKSPACE_LAYOUT_DIR = WORKSPACE_DIR / "layout"

WORKSPACE_MODELS_DIR = WORKSPACE_DIR / "models"

WORKSPACE_MODULE_MANAGER_DIR = WORKSPACE_DIR / "modules"

WORKSPACE_PATIENT_DIR = WORKSPACE_DIR / "patient"


WORKSPACE_COMPONENTS_LOADERS_DIR = WORKSPACE_DIR / "components_loaders"

WORKSPACE_SIDE_PANEL_LOADERS_DIR = (WORKSPACE_COMPONENTS_LOADERS_DIR / "side_panel_loaders")

WORKSPACE_TOOLS_TAB_LOADERS_DIR = (WORKSPACE_COMPONENTS_LOADERS_DIR / "tools_tab_loaders")



WORKSPACE_CONTAINERS_DIR = WORKSPACE_DIR / "containers"

WORKSPACE_HEADER_DIR = (WORKSPACE_CONTAINERS_DIR / "header_container")

WORKSPACE_TOOLBAR_DIR = (WORKSPACE_CONTAINERS_DIR / "toolbar_container")

WORKSPACE_CENTRAL_AREA_DIR = (WORKSPACE_CONTAINERS_DIR / "central_area_container")

WORKSPACE_SIDE_PANEL_DIR = (WORKSPACE_CONTAINERS_DIR / "side_panel_container")

WORKSPACE_STATUS_BAR_DIR = (WORKSPACE_CONTAINERS_DIR / "status_bar")




# ==============================================================================
# VOLUME
# ==============================================================================

VOLUME_DIR = CORE_DIR / "volume"

DICOM_DIR = VOLUME_DIR / "dicom"

DICOM_ENGINES_DIR = DICOM_DIR / "engines"

DICOM_VALIDATORS_DIR = DICOM_DIR / "validators"

EXPORTERS_DIR = VOLUME_DIR / "exporters"

MODELS_DIR = VOLUME_DIR / "models"

PROCESSING_DIR = VOLUME_DIR / "processing"

SEGMENTATION_DIR = VOLUME_DIR / "segmentation"

SEG_ENGINES_DIR = SEGMENTATION_DIR / "engines"

SEG_STRATEGIES_DIR = SEGMENTATION_DIR / "strategies"

VISUALIZATION_DIR = VOLUME_DIR / "visualization"

LUT_DIR = VISUALIZATION_DIR / "lut"

PRESETS_DIR = VISUALIZATION_DIR / "presets"

VIEWER_UTILS_DIR = VISUALIZATION_DIR / "viewer_utils"


# ==============================================================================
# COMMANDS
# ==============================================================================

COMMANDS_DIR = CORE_DIR / "commands"

COMMANDS_BASE_DIR = COMMANDS_DIR / "base"

COMMANDS_SCENE_DIR = COMMANDS_DIR / "scene"

COMMANDS_MESH_DIR = COMMANDS_DIR / "mesh"

COMMANDS_SEGMENTATION_DIR = COMMANDS_DIR / "segmentation"

COMMANDS_TRANSFORMS_DIR = COMMANDS_DIR / "transforms"