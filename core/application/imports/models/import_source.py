from dataclasses import dataclass
from enum import Enum
from ui.settings.localization.translator import tr


@dataclass(frozen=True)
class ImportSourceInfo:
    """Metadata for an import source."""

    name_key: str
    desc_key: str
    icon: str

    @property
    def display_name(self) -> str:
        return tr(self.name_key)

    @property
    def description(self) -> str:
        return tr(self.desc_key)


class ImportSource(Enum):
    """Import sources supported by OpenCMF."""

    PROJECT = ImportSourceInfo(
        name_key="imports.sources.project_manager.name",
        desc_key="imports.sources.project_manager.description",
        icon=":/icons_manager/project_manager.svg",
    )

    FILE = ImportSourceInfo(
        name_key="imports.sources.file.name",
        desc_key="imports.sources.file.description",
        icon=":/icons_manager/folder.svg",
    )

    @property
    def display_name(self) -> str:
        return self.value.display_name

    @property
    def description(self) -> str:
        return self.value.description

    @property
    def icon(self) -> str:
        return self.value.icon