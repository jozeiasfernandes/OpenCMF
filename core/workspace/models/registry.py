from typing import Dict, List, Any
import logging

from core.workspace.models.contracts import IModule
from core.workspace.models.module_factory import ModuleFactory

logger = logging.getLogger(__name__)


class WorkspaceRegistry:
    """Gerencia o registro e ciclo de vida dos módulos ativos no workspace."""

    def __init__(self) -> None:
        self._active_modules: Dict[str, Any] = {}

    def register_active_module(self, module_id: str) -> None:
        """Registra um módulo como ativo na workspace para que possa ser carregado."""
        if module_id not in self._active_modules:
            logger.info(f"[WorkspaceRegistry] Registrando ID de módulo ativo: '{module_id}'")
            # Apenas garante a marcação ou deixa pronto para carregamento sob demanda
            self._active_modules[module_id] = None  # Será instanciado via get_or_create_module

    def get_or_create_module(self, module_id: str) -> Any:
        """Retorna um módulo ativo ou cria um novo se não existir."""
        logger.debug(
            f"[WorkspaceRegistry] Solicitando módulo '{module_id}'. Ativos atuais: {list(self._active_modules.keys())}")

        if module_id not in self._active_modules or self._active_modules[module_id] is None:
            try:
                logger.info(
                    f"[WorkspaceRegistry] Módulo '{module_id}' não instanciado. Solicitando criação via ModuleFactory...")
                instance = ModuleFactory.create(module_id)

                # Validação defensiva robusta (suporta isinstance virtual ou verificação estrutural)
                required_methods = ["inicializar", "get_central_area", "get_side_panel"]
                if not isinstance(instance, IModule) and not all(hasattr(instance, m) for m in required_methods):
                    raise TypeError(f"A instância do módulo '{module_id}' não atende ao contrato do sistema.")

                self._active_modules[module_id] = instance
                logger.info(
                    f"[WorkspaceRegistry] Módulo '{module_id}' instanciado com sucesso e armazenado no registro.")
            except Exception as e:
                logger.error(f"[WorkspaceRegistry] Erro crítico ao instanciar módulo '{module_id}': {e}", exc_info=True)
                raise

        return self._active_modules[module_id]

    # Adicionado método alias para compatibilidade com o WorkspaceModuleManager
    def get_module(self, module_id: str) -> Any:
        """Retorna o módulo ativo pelo ID, criando-o se necessário."""
        return self.get_or_create_module(module_id)

    def unregister(self, module_id: str) -> None:
        """Remove um módulo do registro e realiza sua limpeza."""
        if module_id in self._active_modules:
            logger.info(f"[WorkspaceRegistry] Removendo módulo '{module_id}' do registro.")
            instance = self._active_modules.pop(module_id)

            try:
                if instance and hasattr(instance, "cleanup"):
                    instance.cleanup()
                elif instance and hasattr(instance, "dispose"):
                    instance.dispose()
            except Exception as e:
                logger.warning(f"Erro ao executar limpeza do módulo '{module_id}': {e}")

            ModuleFactory._instances.pop(module_id, None)

    def clear_all(self) -> None:
        """Remove e limpa todos os módulos ativos."""
        logger.info("[WorkspaceRegistry] Limpando todos os módulos ativos da workspace.")
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
        active_list = list(self._active_modules.keys())
        logger.debug(f"[WorkspaceRegistry] list_active_modules chamado. Retornando: {active_list}")
        return active_list