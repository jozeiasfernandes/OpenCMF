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
        logger.debug(f"Dependências compartilhadas atualizadas: {list(dependencies.keys())}")

    @classmethod
    def create(cls, module_id: str, force_new: bool = False, **extra_args) -> IModule:
        if not force_new and module_id in cls._instances:
            return cls._instances[module_id]

        if module_id not in cls._modules:
            msg = f"Módulo '{module_id}' não registrado na Factory."
            logger.error(msg)
            raise ValueError(msg)

        module_class = cls._modules[module_id]

        init_args = {**cls._shared_dependencies, **extra_args}

        try:
            instance = module_class(**init_args)
        except Exception as e:
            # O log de erro agora captura o traceback completo e os argumentos tentados
            logger.error(f"Falha ao instanciar o módulo '{module_id}' com args {list(init_args.keys())}: {e}",
                         exc_info=True)
            raise RuntimeError(f"Erro ao instanciar o módulo '{module_id}': {e}") from e

        if not isinstance(instance, IModule):
            raise TypeError(f"A classe '{module_class.__name__}' não implementa IModule.")

        if not force_new:
            cls._instances[module_id] = instance

        return instance

    @classmethod
    def clear_cache(cls):
        # Limpeza reversa ou via lista para evitar erros durante a iteração
        for module_id in list(cls._instances.keys()):
            instance = cls._instances.pop(module_id)
            if hasattr(instance, "cleanup"):
                try:
                    instance.cleanup()
                except Exception as e:
                    logger.warning(f"Erro no cleanup do módulo '{module_id}': {e}")
        logger.info("Cache da Factory limpo.")