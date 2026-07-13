# core/components/registry.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Type, Optional, Any
from enum import Enum, auto


class ComponentType(Enum):
    TOOL = "tools"
    TOOLBAR = "toolbars"
    SIDE_PANEL = "side_panel"
    CENTRAL_AREA = "central_area"


@dataclass
class ComponentMetadata:
    path: Path
    display_name: str
    component_type: ComponentType
    category: Optional[str] = None
    class_name: Optional[str] = None
    dependencies: Dict[str, Any] = field(default_factory=dict)


class ComponentRegistry:
    """
    Registry centralizado (Singleton) que armazena metadados de todos os componentes
    descobertos pelo Scanner.
    """
    _instance = None
    _components: Dict[ComponentType, Dict[str, ComponentMetadata]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_component(cls, metadata: ComponentMetadata):
        """Registra um componente no catálogo."""
        if metadata.component_type not in cls._components:
            cls._components[metadata.component_type] = {}

        # Usamos o nome do arquivo (stem) como chave única
        key = metadata.path.stem
        cls._components[metadata.component_type][key] = metadata

    @classmethod
    def get_component(cls, component_type: ComponentType, name: str) -> Optional[ComponentMetadata]:
        """Recupera metadados de um componente específico."""
        return cls._components.get(component_type, {}).get(name)

    @classmethod
    def get_components_by_type(cls, component_type: ComponentType) -> Dict[str, ComponentMetadata]:
        """Retorna todos os componentes de um determinado tipo."""
        return cls._components.get(component_type, {})

    @classmethod
    def clear(cls):
        """Limpa o registro (útil para testes ou reinicializações)."""
        cls._components.clear()