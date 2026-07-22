import logging
from typing import Dict, Type, Optional, Any
from .contracts import IModule

logger = logging.getLogger(__name__)

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
            if hasattr(instance, "cleanup"):
                try:
                    instance.cleanup()
                except Exception as e:
                    logger.warning(f"Erro no cleanup do módulo '{module_id}': {e}")
            elif hasattr(instance, "dispose"):  # Mantém compatibilidade retroativa opcional
                try:
                    instance.dispose()
                except Exception as e:
                    logger.warning(f"Erro no dispose do módulo '{module_id}': {e}")
        logger.info("Cache da Factory limpo.")