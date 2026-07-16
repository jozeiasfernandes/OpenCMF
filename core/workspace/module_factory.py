import logging 
from typing import Dict, Type, Optional, Any
from .contracts import IModule

logger = logging.getLogger(__name__)


class ModuleFactory:
    _modules: Dict[str, Type[IModule]] = {}
    _instances: Dict[str, IModule] = {}
    _shared_dependencies: Dict[str, Any] = {}

    @classmethod
    def register(cls, module_id: str, module_class: Type[IModule]):
        cls._modules[module_id] = module_class
        logger.debug(f"Módulo '{module_id}' registrado com sucesso.")

    @classmethod
    def set_shared_dependencies(cls, **dependencies):
        cls._shared_dependencies.update(dependencies)

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
            init_args = {**cls._shared_dependencies, **extra_args}
            instance = module_class(**init_args)
        except Exception as e:
            # Agora 'logger' é reconhecido aqui!
            logger.error(f"Falha ao instanciar o módulo '{module_id}': {e}", exc_info=True)
            raise RuntimeError(f"Erro ao instanciar o módulo '{module_id}': {e}") from e

        if not isinstance(instance, IModule):
            raise TypeError(f"A classe '{module_class.__name__}' não implementa IModule.")

        if not force_new:
            cls._instances[module_id] = instance

        return instance

    @classmethod
    def clear_cache(cls):
        for module_id, instance in list(cls._instances.items()):
            if hasattr(instance, "cleanup"):
                instance.cleanup()
            del cls._instances[module_id]
        logger.info("Cache da Factory limpo.")