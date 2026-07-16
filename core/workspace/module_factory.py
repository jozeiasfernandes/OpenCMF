from typing import Dict, Type, Optional, Any
from .contracts import IModule

class ModuleFactory:
    """
    Registry global e Factory de módulos com suporte a Injeção de Dependência.
    """
    _modules: Dict[str, Type[IModule]] = {}
    _instances: Dict[str, IModule] = {}
    _shared_dependencies: Dict[str, Any] = {} # Armazena bus, registry, etc.

    @classmethod
    def register(cls, module_id: str, module_class: Type[IModule]):
        cls._modules[module_id] = module_class

    @classmethod
    def set_shared_dependencies(cls, **dependencies):
        """Define dependências globais que serão passadas para todos os módulos."""
        cls._shared_dependencies.update(dependencies)

    @classmethod
    def create(cls, module_id: str, force_new: bool = False, **extra_args) -> IModule:
        """
        Cria uma instância do módulo passando as dependências registradas
        e argumentos extras (ex: pasta_paciente).
        """
        if not force_new and module_id in cls._instances:
            return cls._instances[module_id]

        if module_id not in cls._modules:
            raise ValueError(f"Módulo '{module_id}' não registrado na Factory.")

        try:
            # Combina dependências globais com argumentos específicos deste chamado
            init_args = {**cls._shared_dependencies, **extra_args}
            instance = cls._modules[module_id](**init_args)
        except Exception as e:
            raise RuntimeError(f"Erro ao instanciar o módulo '{module_id}': {e}")

        if not isinstance(instance, IModule):
            raise TypeError(f"Classe para '{module_id}' não implementa IModule!")

        cls._instances[module_id] = instance
        return instance

    @classmethod
    def clear_cache(cls):
        for instance in cls._instances.values():
            if hasattr(instance, "cleanup"):
                instance.cleanup()
        cls._instances.clear()

    @classmethod
    def get_available_modules(cls) -> list[str]:
        return list(cls._modules.keys())