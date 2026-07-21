import logging
from pathlib import Path
from typing import Dict, Any, Optional
from core.components.registry import ComponentRegistry, ComponentType, ComponentMetadata
from core.components.scanner import ComponentScanner
from core.loaders.loader_components import ComponentLoader

logger = logging.getLogger("ComponentManager")


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


import logging
from typing import Dict, Type, Optional, Any
from .contracts import IModule

logger = logging.getLogger("ModuleFactory")

class ModuleFactory:
    _modules: Dict[str, Type[IModule]] = {}
    _instances: Dict[str, IModule] = {}
    _context: Optional[Any] = None

    @classmethod
    def register(cls, module_id: str, module_class: Type[IModule]):
        cls._modules[module_id] = module_class
        logger.debug(f"Módulo '{module_id}' registrado com sucesso.")

    @classmethod
    def set_context(cls, context: Any):
        """Define o contexto único que será injetado em todos os módulos."""
        cls._context = context
        logger.debug("Contexto da aplicação definido na Factory.")

    @classmethod
    def create(cls, module_id: str, force_new: bool = False, **extra_args) -> IModule:
        if not force_new and module_id in cls._instances:
            return cls._instances[module_id]

        if module_id not in cls._modules:
            msg = f"Módulo '{module_id}' não registrado na Factory."
            logger.error(msg)
            raise ValueError(msg)

        module_class = cls._modules[module_id]

        try:
            instance = module_class(context=cls._context, **extra_args)
        except Exception as e:
            logger.error(f"Falha ao instanciar o módulo '{module_id}': {e}", exc_info=True)
            raise RuntimeError(f"Erro ao instanciar o módulo '{module_id}': {e}") from e

        if not isinstance(instance, IModule):
            raise TypeError(f"A classe '{module_class.__name__}' não implementa IModule.")

        if not force_new:
            cls._instances[module_id] = instance

        return instance

    @classmethod
    def clear_cache(cls):
        for module_id in list(cls._instances.keys()):
            instance = cls._instances.pop(module_id)
            if hasattr(instance, "dispose"):
                try:
                    instance.dispose()
                except Exception as e:
                    logger.warning(f"Erro no dispose do módulo '{module_id}': {e}")
        logger.info("Cache da Factory limpo.")