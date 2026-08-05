from __future__ import annotations

import sys
from pathlib import Path


# ==============================================================================
# BASE
# ==============================================================================

def get_project_root() -> Path:
    """
    Retorna a raiz do projeto.

    Compatível com execução normal e PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    # Como o arquivo está na raiz do projeto (C:\OpenCMF\list_paths.py),
    # o diretório pai direto já é a raiz.
    return Path(__file__).resolve().parent


BASE_DIR = get_project_root()


# ==============================================================================
# RUNTIME (Declarados antes para uso em funções utilitárias)
# ==============================================================================

LOGS_DIR = BASE_DIR / "logs"

CACHE_DIR = BASE_DIR / "cache"

TEMP_DIR = BASE_DIR / "temp"

PATIENTS_DIR = BASE_DIR / "patients"


# ==============================================================================
# UTILITÁRIOS
# ==============================================================================

def resource(*parts: str) -> Path:
    """
    Retorna um caminho relativo à raiz do projeto.

    Exemplo:
        resource("appearance", "icons", "save.svg")
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

CONFIG_FILE = BASE_DIR / "config.json"

CONFIG_FILE_PATH = CONFIG_FILE

CORE_DIR = BASE_DIR / "core"

SETTINGS_DIR = BASE_DIR / "core" / "settings"

TRANSLATIONS_DIR = SETTINGS_DIR / "localization" / "translations"

SHORTCUTS_FILE = SETTINGS_DIR / "shortcuts" / "shortcuts.json"

SHORTCUTS_FILE_PATH = SHORTCUTS_FILE

SETTINGS_HELP_DIR = SETTINGS_DIR / "help"

SETTINGS_ICONS_DIR = SETTINGS_DIR / "icons"

SETTINGS_LOCALIZATION_DIR = SETTINGS_DIR / "localization"

SETTINGS_LOGS_DIR = SETTINGS_DIR / "logs"

SETTINGS_LOGS_ARCHIVES_DIR = SETTINGS_LOGS_DIR / "archives"

SETTINGS_PAGE_TABS_DIR = SETTINGS_DIR / "settings_page_tabs"

SETTINGS_SHORTCUTS_DIR = SETTINGS_DIR / "shortcuts"

SETTINGS_THEMES_DIR = SETTINGS_DIR / "themes"


# ==============================================================================
# PACIENTES
# ==============================================================================

FLOWS_DIR = BASE_DIR / "flows"

DEFAULT_FLOW_FILE = FLOWS_DIR / "default_flow.json"

REGISTRATION_FLOW_FILE = FLOWS_DIR / "new_patient_registration.json"

REGISTRATION_FLOW_NAME = REGISTRATION_FLOW_FILE.name


# ==============================================================================
# APPEARANCE
# ==============================================================================

APPEARANCE_DIR = BASE_DIR / "appearance"

ICONS_DIR = APPEARANCE_DIR / "icons"

ICONS_THEMES_DIR = APPEARANCE_DIR / "icons_themes"

THEMES_DIR = APPEARANCE_DIR / "themes"


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

WORKSPACE_COMPONENTS_LOADERS_DIR = WORKSPACE_DIR / "components_loaders"

WORKSPACE_SIDE_PANEL_LOADERS_DIR = (
    WORKSPACE_COMPONENTS_LOADERS_DIR / "side_panel_loaders"
)

WORKSPACE_TOOLS_TAB_LOADERS_DIR = (
    WORKSPACE_COMPONENTS_LOADERS_DIR / "tools_tab_loaders"
)

WORKSPACE_CONTAINERS_DIR = WORKSPACE_DIR / "containers"

WORKSPACE_CENTRAL_AREA_DIR = (
    WORKSPACE_CONTAINERS_DIR / "central_area_container"
)

WORKSPACE_HEADER_DIR = (
    WORKSPACE_CONTAINERS_DIR / "header_container"
)

WORKSPACE_SIDE_PANEL_DIR = (
    WORKSPACE_CONTAINERS_DIR / "side_panel_container"
)

WORKSPACE_STATUS_BAR_DIR = (
    WORKSPACE_CONTAINERS_DIR / "status_bar"
)

WORKSPACE_TOOLBAR_DIR = (
    WORKSPACE_CONTAINERS_DIR / "toolbar_container"
)

WORKSPACE_LAYOUT_DIR = WORKSPACE_DIR / "layout"

WORKSPACE_MODELS_DIR = WORKSPACE_DIR / "models"

WORKSPACE_MODULE_MANAGER_DIR = WORKSPACE_DIR / "module_manager"

WORKSPACE_PATIENT_DIR = WORKSPACE_DIR / "patient"


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