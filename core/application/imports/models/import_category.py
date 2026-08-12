from dataclasses import dataclass
from enum import Enum
from ui.settings.localization.translator import tr


@dataclass(frozen=True)
class CategoryInfo:
    """Metadata for an import category."""

    name_key: str
    icon: str
    supports_project: bool
    supports_file: bool
    supports_online: bool = False

    @property
    def display_name(self) -> str:
        return tr(self.name_key)


class ImportCategory(Enum):
    """Import categories supported by OpenCMF."""

    VOLUME = CategoryInfo(
        name_key="imports.categories.volume",
        icon=":/icons_manager/volume.svg",
        supports_project=True,
        supports_file=True,
    )

    RADIOGRAPHY = CategoryInfo(
        name_key="imports.categories.radiography",
        icon=":/icons_manager/radiography.svg",
        supports_project=True,
        supports_file=True,
    )

    SCAN = CategoryInfo(
        name_key="imports.categories.scan",
        icon=":/icons_manager/scan.svg",
        supports_project=True,
        supports_file=True,
    )

    PHOTO = CategoryInfo(
        name_key="imports.categories.photo",
        icon=":/icons_manager/photo.svg",
        supports_project=True,
        supports_file=True,
    )

    MESH = CategoryInfo(
        name_key="imports.categories.mesh",
        icon=":/icons_manager/mesh.svg",
        supports_project=True,
        supports_file=True,
    )

    LIBRARY = CategoryInfo(
        name_key="imports.categories.library",
        icon=":/icons_manager/library.svg",
        supports_project=True,
        supports_file=False,
        supports_online=True,
    )

    FACIAL_IMPLANT = CategoryInfo(
        name_key="imports.categories.facial_implant",
        icon=":/icons_manager/facial_implant.svg",
        supports_project=True,
        supports_file=False,
        supports_online=True,
    )

    DENTAL_IMPLANT = CategoryInfo(
        name_key="imports.categories.dental_implant",
        icon=":/icons_manager/dental_implant.svg",
        supports_project=True,
        supports_file=False,
        supports_online=True,
    )

    @property
    def display_name(self) -> str:
        return self.value.display_name

    @property
    def icon(self) -> str:
        return self.value.icon

    @property
    def supports_project(self) -> bool:
        return self.value.supports_project

    @property
    def supports_file(self) -> bool:
        return self.value.supports_file

    @property
    def supports_online(self) -> bool:
        return self.value.supports_online