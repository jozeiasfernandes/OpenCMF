from typing import Dict, Type
from .contracts import IModule

class ModuleFactory:
    """
    Registry global e Factory de módulos.
    """
    _modules: Dict[str, Type[IModule]] = {}

    @classmethod
    def register(cls, module_id: str, module_class: Type[IModule]):
        cls._modules[module_id] = module_class

    @classmethod
    def create(cls, module_id: str) -> IModule:
        if module_id not in cls._modules:
            raise ValueError(f"Módulo '{module_id}' não registrado na Factory.")

        # Instanciamos a classe
        module_instance = cls._modules[module_id]()

        # VALIDAÇÃO DE CONTRATO (Garantia de segurança)
        if not isinstance(module_instance, IModule):
            raise TypeError(
                f"A classe registrada para '{module_id}' não implementa o contrato IModule!"
            )

        return module_instance

    @classmethod
    def get_available_modules(cls) -> list[str]:
        return list(cls._modules.keys())