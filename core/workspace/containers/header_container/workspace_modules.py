import logging
from typing import Optional
from core.workspace.models.contracts import IModule
from core.workspace.services.layout import ModuleDistributor

logger = logging.getLogger("OpenCMF.Workspace.Modules")

class WorkspaceModulesMixin:
    """Gerencia o carregamento, troca e ciclo de vida dos módulos."""

    def on_module_changed(self, module_id: str):
        """Troca o módulo ativo e distribui seus componentes."""
        try:
            ModuleDistributor.cleanup(
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            module = self.registry.get_or_create_module(module_id)
            ModuleDistributor.distribute(
                module,
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            if self.state.current_patient and hasattr(module, "inicializar"):
                module.inicializar(self.state.current_patient)

            logger.info(f"Módulo '{module_id}' carregado com sucesso.")
            self.status_bar_manager.showMessage(f"Módulo '{module_id}' carregado.", 3000)

        except Exception as e:
            logger.error(f"Erro crítico ao carregar módulo '{module_id}': {e}", exc_info=True)
            self.status_bar_manager.showMessage("Erro ao carregar módulo", 5000)

    def get_modulo_ativo(self) -> Optional[IModule]:
        """Retorna o módulo correspondente à aba atualmente selecionada."""
        current_index = self.header.tab_bar.currentIndex()
        if current_index >= 0:
            module_id = self.header.tab_bar.tabData(current_index)
            if module_id:
                return self.registry.get_or_create_module(module_id)
        return None