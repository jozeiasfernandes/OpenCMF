from pathlib import Path
from typing import Dict, Any, Optional
from core.components.registry import ComponentRegistry, ComponentType, ComponentMetadata
from core.components.scanner import ComponentScanner
from core.loaders.loader_components import ComponentLoader


class ComponentManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.components_path = Path(__file__).resolve().parent.parent / "components"
        self._scanner = ComponentScanner(self.components_path)
        self._registry = ComponentRegistry()
        self._cache: Dict[str, Any] = {}

    def initialize(self):
        if not self._cache and not self._registry.get_components_by_type(ComponentType.TOOL):
            self._scanner.scan_all()

    def get_component_metadata(self, component_type: ComponentType, name: str) -> Optional[ComponentMetadata]:
        return self._registry.get_component(component_type, name)

    def load_component_instance(self, component_type: ComponentType, name: str, context: Any) -> Optional[Any]:
        cache_key = f"{component_type.value}:{name}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        metadata = self._registry.get_component(component_type, name)
        if not metadata:
            return None

        instance = ComponentLoader.carregar(metadata.path, context)

        if instance:
            self._cache[cache_key] = instance

        return instance

    def clear_cache(self, component_type: Optional[ComponentType] = None):
        if component_type:
            keys_to_del = [k for k in self._cache if k.startswith(component_type.value)]
            for k in keys_to_del:
                del self._cache[k]
        else:
            self._cache.clear()