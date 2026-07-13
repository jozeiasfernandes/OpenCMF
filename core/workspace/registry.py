from typing import Dict, List
from .contracts import IModule
from .module_factory import ModuleFactory

class WorkspaceRegistry:
    """
    Gerencia o ciclo de vida dos módulos ativos no Workspace atual.
    """
    def __init__(self):
        # Apenas mantém referência dos módulos que o workspace carregou
        self._active_modules: Dict[str, IModule] = {}

    def get_or_create_module(self, module_id: str) -> IModule:
        if module_id not in self._active_modules:
            # Delega a criação para a Factory
            self._active_modules[module_id] = ModuleFactory.create(module_id)
        return self._active_modules[module_id]

    def unregister(self, module_id: str):
        """Remove o módulo e dispara o cleanup."""
        if module_id in self._active_modules:
            instance = self._active_modules.pop(module_id)
            instance.cleanup()
            # Opcional: Se a Factory tiver cache, talvez queira limpar lá também:
            # ModuleFactory.remove_from_cache(module_id)

    def clear_all(self):
        """Limpa todos os módulos ativos de forma segura."""
        module_ids = list(self._active_modules.keys())
        for module_id in module_ids:
            try:
                self.unregister(module_id)
            except Exception as e:
                print(f"Erro ao limpar o módulo {module_id}: {e}")

    def is_active(self, module_id: str) -> bool:
        return module_id in self._active_modules

    def list_active_modules(self) -> List[str]:
        return list(self._active_modules.keys())