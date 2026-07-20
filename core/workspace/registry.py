from typing import Dict, List
import logging

from .contracts import IModule
from .module_factory import ModuleFactory

logger = logging.getLogger(__name__)


class WorkspaceRegistry:
    """Gerencia o registro e ciclo de vida dos módulos ativos no workspace."""

    def __init__(self) -> None:
        self._active_modules: Dict[str, IModule] = {}

    def get_or_create_module(self, module_id: str) -> IModule:
        """Retorna um módulo ativo ou cria um novo se não existir."""
        if module_id not in self._active_modules:
            try:
                instance = ModuleFactory.create(module_id)

                # Validação defensiva extra do contrato IModule
                if not isinstance(instance, IModule):
                    raise TypeError(f"A instância do módulo '{module_id}' não implementa o contrato IModule.")

                self._active_modules[module_id] = instance
            except Exception as e:
                logger.error(f"Erro crítico ao instanciar módulo '{module_id}': {e}", exc_info=True)
                raise

        return self._active_modules[module_id]

    def unregister(self, module_id: str) -> None:
        """Remove um módulo do registro e realiza sua limpeza."""
        if module_id in self._active_modules:
            instance = self._active_modules.pop(module_id)

            try:
                if hasattr(instance, "cleanup"):
                    instance.cleanup()
                elif hasattr(instance, "dispose"):
                    instance.dispose()
            except Exception as e:
                logger.warning(f"Erro ao executar limpeza do módulo '{module_id}': {e}")

            ModuleFactory._instances.pop(module_id, None)

    def clear_all(self) -> None:
        """Remove e limpa todos os módulos ativos."""
        module_ids = list(self._active_modules.keys())
        for module_id in module_ids:
            try:
                self.unregister(module_id)
            except Exception as e:
                logger.warning(f"Erro ao limpar o módulo '{module_id}': {e}")

    def is_active(self, module_id: str) -> bool:
        """Verifica se um módulo está ativo."""
        return module_id in self._active_modules

    def list_active_modules(self) -> List[str]:
        """Retorna a lista de IDs dos módulos atualmente ativos."""
        return list(self._active_modules.keys())