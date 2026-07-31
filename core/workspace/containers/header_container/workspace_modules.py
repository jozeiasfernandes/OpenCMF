import logging
from typing import Optional
from core.workspace.models.contracts import IModule
from core.workspace.layout.layout import ModuleDistributor

logger = logging.getLogger("OpenCMF.Workspace.Modules")


class WorkspaceModulesMixin:
    """Gerencia o carregamento, troca e ciclo de vida dos módulos."""

    def on_module_changed(self, module_id: str):
        """Troca o módulo ativo e distribui seus componentes de forma limpa, evitando inicializações duplicadas."""
        try:
            # 1. Limpa os componentes do módulo anterior
            ModuleDistributor.cleanup(
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            # 2. Obtém ou cria o novo módulo
            module = self.registry.get_or_create_module(module_id)
            if not module:
                logger.warning(f"Não foi possível instanciar o módulo '{module_id}'.")
                return

            # 3. Distribui os novos componentes na interface
            ModuleDistributor.distribute(
                module,
                self.toolbar_manager,
                self.side_manager,
                self.central_manager
            )

            # 4. Obtém o path do paciente de forma robusta
            patient_path = getattr(self, "current_patient_path", None)
            if not patient_path and hasattr(self, "state") and hasattr(self.state, "current_patient"):
                patient_path = self.state.current_patient

            # 5. Inicializa o módulo apenas se houver um patient_path válido
            # e evita chamadas redundantes checando o estado interno do módulo
            if patient_path and hasattr(module, "inicializar"):
                last_initialized = getattr(module, "_last_initialized_path", None)
                if last_initialized != patient_path:
                    module.inicializar(patient_path)
                    module._last_initialized_path = patient_path
                    logger.info(f"Módulo '{module_id}' inicializado com o paciente: {patient_path}")
                else:
                    logger.debug(f"Módulo '{module_id}' já estava inicializado para o paciente: {patient_path}")

            logger.info(f"Módulo '{module_id}' carregado com sucesso.")
            self.status_bar_manager.showMessage(f"Módulo '{module_id}' carregado.", 3000)

        except Exception as e:
            logger.error(f"Erro crítico ao carregar módulo '{module_id}': {e}", exc_info=True)
            self.status_bar_manager.showMessage("Erro ao carregar módulo", 5000)

    def get_modulo_ativo(self) -> Optional[IModule]:
        """Retorna o módulo atualmente ativo se já estiver instanciado, evitando criação acidental."""
        current_index = self.header.tab_bar.currentIndex()
        if current_index >= 0:
            module_id = self.header.tab_bar.tabData(current_index)
            if module_id and hasattr(self, "registry") and hasattr(self.registry, "modules"):
                return self.registry.modules.get(module_id)
        return None