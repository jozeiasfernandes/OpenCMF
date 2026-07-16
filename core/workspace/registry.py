from typing import Dict, List

import logging

from .contracts import IModule
from .module_factory import ModuleFactory

logger = logging.getLogger(__name__)


class WorkspaceRegistry:

    def __init__(self) -> None:
        self._active_modules: Dict[str, IModule] = {}

    def get_or_create_module(self, module_id: str) -> IModule:
        if module_id not in self._active_modules:
            try:
                self._active_modules[module_id] = ModuleFactory.create(module_id)
            except Exception as e:
                logger.error(f"Erro crítico ao instanciar módulo '{module_id}': {e}")
                raise

        return self._active_modules[module_id]

    def unregister(self, module_id: str) -> None:
        if module_id in self._active_modules:
            instance = self._active_modules.pop(module_id)
            instance.cleanup()
            ModuleFactory._instances.pop(module_id, None)

    def clear_all(self) -> None:
        module_ids = list(self._active_modules.keys())
        for module_id in module_ids:
            try:
                self.unregister(module_id)
            except Exception as e:
                logger.warning(f"Erro ao limpar o módulo '{module_id}': {e}")

    def is_active(self, module_id: str) -> bool:
        return module_id in self._active_modules

    def list_active_modules(self) -> List[str]:
        return list(self._active_modules.keys())