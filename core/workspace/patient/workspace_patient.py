from typing import Any

class WorkspacePatientMixin:
    """Gerencia o estado e o vínculo do paciente com os módulos ativos."""

    def set_patient_path(self, path: str):
        """Atualiza o path do paciente evitando chamadas redundantes."""
        if self.current_patient_path == path:
            return
        self.current_patient_path = path

        if hasattr(self, "state"):
            self.state.current_patient = path

        if modulo := self.get_modulo_ativo():
            self._safe_inicializar(modulo)

    def _safe_inicializar(self, instancia: Any):
        """Inicializa o módulo de forma segura caso o path seja diferente."""
        if not self.current_patient_path:
            return

        path_modulo = getattr(instancia, 'pasta_paciente', None)
        if str(path_modulo) != str(self.current_patient_path):
            if hasattr(instancia, 'inicializar'):
                instancia.initialize(self.current_patient_path)