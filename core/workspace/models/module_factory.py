import logging
from typing import Dict, Type, Optional, Any
from core.workspace.models.contracts import IModule

logger = logging.getLogger(__name__)


class ModuleFactory:
    _modules: Dict[str, Type[IModule]] = {}
    _instances: Dict[str, IModule] = {}
    _context: Optional[Any] = None

    @classmethod
    def register(cls, module_id: str, module_class: Type[IModule]):
        cls._modules[module_id] = module_class
        logger.info(
            f"[ModuleFactory] Módulo ID '{module_id}' registrado com sucesso usando a classe '{module_class.__name__}'. Módulos registrados atualmente: {list(cls._modules.keys())}")

    @classmethod
    def set_context(cls, context: Any):
        """Define o contexto único que será injetado em todos os módulos."""
        cls._context = context
        logger.info(f"[ModuleFactory] Contexto da aplicação definido na Factory: {type(context).__name__}")

    @classmethod
    def create(cls, module_id: str, force_new: bool = False, **extra_args) -> IModule:
        logger.debug(f"[ModuleFactory] Solicitação de criação para o módulo ID: '{module_id}' (force_new={force_new}).")

        if not force_new and module_id in cls._instances:
            logger.debug(f"[ModuleFactory] Retornando instância em cache para o módulo '{module_id}'.")
            return cls._instances[module_id]

        if module_id not in cls._modules:
            msg = f"[ModuleFactory] ERRO CRÍTICO: O módulo ID '{module_id}' NÃO está registrado na Factory! Módulos disponíveis no registro: {list(cls._modules.keys())}"
            logger.error(msg)
            raise ValueError(msg)

        module_class = cls._modules[module_id]
        logger.info(f"[ModuleFactory] Instanciando a classe '{module_class.__name__}' para o ID '{module_id}'...")

        try:
            if cls._context is not None:
                try:
                    instance = module_class(context=cls._context, **extra_args)
                    logger.debug(f"[ModuleFactory] Instância criada com sucesso passando o 'context'.")
                except TypeError as te:
                    logger.warning(
                        f"[ModuleFactory] A classe '{module_class.__name__}' recusou o argumento 'context' ({te}). Tentando instanciar sem argumentos contextuais...")
                    instance = module_class(**extra_args)
            else:
                instance = module_class(**extra_args)
                logger.debug(f"[ModuleFactory] Instância criada com sucesso sem contexto definido.")
        except Exception as e:
            logger.error(f"[ModuleFactory] Falha ao instanciar a classe do módulo '{module_id}': {e}", exc_info=True)
            raise RuntimeError(f"Erro ao instanciar o módulo '{module_id}': {e}") from e

        if not isinstance(instance, IModule):
            err_msg = f"[ModuleFactory] ERRO DE CONTRATO: A classe '{module_class.__name__}' instanciada para '{module_id}' não atende ao protocolo IModule."
            logger.error(err_msg)
            raise TypeError(err_msg)

        if not force_new:
            cls._instances[module_id] = instance
            logger.info(f"[ModuleFactory] Módulo '{module_id}' armazenado com sucesso no cache de instâncias.")

        return instance

    @classmethod
    def clear_cache(cls):
        logger.info("[ModuleFactory] Limpando cache de instâncias dos módulos...")
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
        logger.info("[ModuleFactory] Cache da Factory limpo com sucesso.")