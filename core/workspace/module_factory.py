from typing import Dict, Type, Optional, Any
from .contracts import IModule

class ModuleFactory:
    """
    Registry global e Factory de módulos.
    """
    _modules: Dict[str, Type[IModule]] = {}
    _instances: Dict[str, IModule] = {}  # Cache de instâncias (Singleton por sessão)

    @classmethod
    def register(cls, module_id: str, module_class: Type[IModule]):
        cls._modules[module_id] = module_class

    @classmethod
    def create(cls, module_id: str, force_new: bool = False) -> IModule:
        # Se já existe instância e não forçar nova, retorna a existente (Cache)
        if not force_new and module_id in cls._instances:
            return cls._instances[module_id]

        if module_id not in cls._modules:
            raise ValueError(f"Módulo '{module_id}' não registrado na Factory.")

        try:
            # Instanciação com tratamento de erro
            instance = cls._modules[module_id]()
        except Exception as e:
            raise RuntimeError(f"Erro ao instanciar o módulo '{module_id}': {e}")

        # Validação de contrato
        if not isinstance(instance, IModule):
            raise TypeError(f"Classe para '{module_id}' não implementa IModule!")

        cls._instances[module_id] = instance
        return instance

    @classmethod
    def clear_cache(cls):
        """Limpa instâncias ativas (útil ao fechar paciente ou resetar workspace)."""
        for instance in cls._instances.values():
            if hasattr(instance, "cleanup"):
                instance.cleanup()
        cls._instances.clear()

    @classmethod
    def get_available_modules(cls) -> list[str]:
        return list(cls._modules.keys())