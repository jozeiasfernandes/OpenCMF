import logging
from typing import Optional

# Workspace
from core.workspace.models.contracts import IModule
from core.workspace.layout.layout import ModuleDistributor

# Logs
logger = logging.getLogger("OpenCMF.Workspace.Modules")


class WorkspaceModulesMixin:
    """Gerencia o carregamento, troca e ciclo de vida dos módulos."""

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    def on_module_changed(self, module_id: str):
        """Troca o módulo ativo e distribui seus componentes."""
        try:
            ModuleDistributor.cleanup(
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            module = self.registry.get_or_create_module(module_id)
            if not module:
                logger.warning(f"Não foi possível instanciar o módulo '{module_id}'.")
                return

            ModuleDistributor.distribute(
                module,
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            patient_path = getattr(self, "current_patient_path", None)
            if not patient_path and hasattr(self, "state") and hasattr(self.state, "current_patient"):
                patient_path = self.state.current_patient

            if patient_path and hasattr(module, "inicializar"):
                last_initialized = getattr(module, "_last_initialized_path", None)
                if last_initialized != patient_path:
                    module.inicializar(patient_path)
                    module._last_initialized_path = patient_path
                    logger.info(f"Módulo '{module_id}' inicializado com o paciente: {patient_path}")
                else:
                    logger.debug(f"Módulo '{module_id}' já estava inicializado para o paciente: {patient_path}")

            logger.info(f"Módulo '{module_id}' carregado com sucesso.")
            if hasattr(self, 'status_bar_manager') and self.status_bar_manager:
                self.status_bar_manager.showMessage(f"Módulo '{module_id}' carregado.", 3000)

        except Exception as e:
            logger.error(f"Erro crítico ao carregar módulo '{module_id}': {e}", exc_info=True)
            if hasattr(self, 'status_bar_manager') and self.status_bar_manager:
                self.status_bar_manager.showMessage("Erro ao carregar módulo", 5000)

    def get_active_module(self) -> Optional[IModule]:
        """Retorna o módulo atualmente ativo."""
        try:
            if hasattr(self, "tab_controller") and self.tab_controller:
                current_widget = self.tab_controller.container.currentWidget()
                if current_widget and hasattr(self, "_widget_to_module_id") and current_widget in self._widget_to_module_id:
                    module_id = self._widget_to_module_id[current_widget]
                    if hasattr(self, "registry") and hasattr(self.registry, "get_or_create_module"):
                        return self.registry.get_or_create_module(module_id)

            current_index = self.tab_controller.container.currentIndex()
            if current_index >= 0 and hasattr(self, "registry"):
                active_modules = self.registry.list_active_modules()
                if current_index < len(active_modules):
                    module_id = active_modules[current_index]
                    return self.registry.get_module(module_id)
        except Exception as e:
            logger.error(f"Erro ao obter módulo ativo no manager: {e}")
        return None