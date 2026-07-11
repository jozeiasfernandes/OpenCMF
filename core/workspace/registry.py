from typing import Dict, List
from .contracts import IModule
from .module_factory import ModuleFactory

class WorkspaceRegistry:
    def __init__(self):
        self._modules: Dict[str, IModule] = {}

    def get_or_create_module(self, module_id: str) -> IModule:
        if module_id not in self._modules:
            module_instance = ModuleFactory.create(module_id)
            self._modules[module_id] = module_instance
        return self._modules[module_id]

    def unregister(self, module_id: str):
        if module_id in self._modules:
            instance = self._modules.pop(module_id)
            instance.cleanup()

    def is_active(self, module_id: str) -> bool:
        return module_id in self._modules

    def list_active_modules(self) -> List[str]:
        return list(self._modules.keys())