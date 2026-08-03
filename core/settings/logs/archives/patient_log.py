import logging
from typing import Dict, Any, Optional
from settings.logs.base_logger import setup_logger

# Configura o logger específico para o painel de debug/logs do paciente
logger = setup_logger("OpenCMF.Patient.Debug", filename=None)


class Patient_Logger:
    """
    Classe de logs e inspeção de estado do Paciente ativo no OpenCMF.
    Monitora dados do info.json, caminhos, integridade e metadados da sessão.
    """

    def __init__(self, patient_manager: Optional[Any] = None):
        self.patient_manager = patient_manager

    def inspect_full_state(self) -> Dict[str, Any]:
        """Coleta um relatório completo e detalhado do paciente e estado atual da sessão."""
        if not self.patient_manager:
            return {"status": "PatientManager não vinculado"}

        current_path = self.patient_manager.current_path
        data = self.patient_manager.data

        report = {
            "session_info": {
                "current_patient_path": current_path,
                "has_active_patient": bool(current_path)
            },
            "patient_metadata": data if data else {}
        }
        return report

    def log_full_state(self, level: int = logging.INFO) -> None:
        """Gera e registra o relatório completo do paciente formatado em bloco único."""
        state = self.inspect_full_state()

        report_lines = [
            "=" * 60,
            "🔍 [PATIENT DEBUG INSPECTOR] - RELATÓRIO DE ESTADO",
            "=" * 60,
            f"• Sessão & Caminho:\n{self._format_dict(state.get('session_info', {}))}",
            f"• Dados / Metadados do Paciente (info.json):\n{self._format_dict(state.get('patient_metadata', {}))}",
            "=" * 60
        ]

        logger.log(level, "\n" + "\n".join(report_lines))

    @staticmethod
    def _format_dict(data: Any, indent: int = 4) -> str:
        """Formata dicionários e listas de forma limpa e estruturada para os logs."""
        import pprint

        if not data:
            return "{}" if isinstance(data, dict) else "[]"

        return pprint.pformat(
            data,
            indent=indent,
            width=70,
            compact=False,
            sort_dicts=False
        )


__all__ = [
    "Patient_Logger",
]