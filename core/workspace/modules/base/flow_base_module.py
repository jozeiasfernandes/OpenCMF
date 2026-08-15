from typing import List, Dict, Any, Optional


from core.workspace.modules.base.base_module import ModuleBase

class FlowModuleBase(ModuleBase):
    """
    Uma base especializada para módulos que requerem navegação entre etapas.
    Herdar de ModuleBase garante a integração total com o Workspace.
    """

    def __init__(self, context, parent=None):
        # Chama o construtor do ModuleBase (UI, EventBus, Logger)
        super().__init__(context, parent)

        # Inicializa a lógica de controle de fluxo
        self.sequencia = context.get("sequencia", [])
        self.configuracoes = context.get("configuracoes", {})
        self.indice_atual = 0

    @property
    def total_stages(self) -> int:
        return len(self.sequencia)

    @property
    def current_stage(self) -> Optional[str]:
        if 0 <= self.indice_atual < self.total_stages:
            return self.sequencia[self.indice_atual]
        return None

    def advance(self) -> bool:
        if self.indice_atual < self.total_stages - 1:
            self.indice_atual += 1
            self.on_stage_changed()
            return True
        return False

    def retreat(self) -> bool:
        if self.indice_atual > 0:
            self.indice_atual -= 1
            self.on_stage_changed()
            return True
        return False

    def on_stage_changed(self):
        pass