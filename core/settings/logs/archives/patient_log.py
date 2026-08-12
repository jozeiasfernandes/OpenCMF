import logging
from typing import Dict, Any, Optional
from settings.logs.base_logger import setup_logger

logger = setup_logger("OpenCMF.Patient.Debug", filename=None)


class Patient_Logger:
    """Logs e inspeção do estado do Paciente ativo no OpenCMF."""

    def __init__(self, patient_manager: Optional[Any] = None):
        self.patient_manager = patient_manager

    # =========================================================================
    # INSPECTION & REPORTING
    # =========================================================================
    def inspect_full_state(self) -> Dict[str, Any]:
        """Coleta o estado completo filtrando dados vazios."""
        if not self.patient_manager:
            return {"status": "PatientManager não vinculado"}

        current_path = getattr(self.patient_manager, "current_path", "")
        data = getattr(self.patient_manager, "data", {})

        report = {}

        session_info = {
            "path": current_path,
            "has_active_patient": bool(current_path)
        }
        if session_info["has_active_patient"]:
            report["Sessão"] = session_info

        if data:
            report["Metadados (info.json)"] = data

        return report

    def log_full_state(self, level: int = logging.INFO) -> None:
        """Gera um relatório estruturado e minimalista."""
        state = self.inspect_full_state()

        if not state or (len(state) == 1 and "status" in state):
            logger.log(level, f"👤 [PATIENT] {state.get('status', 'Estado vazio ou paciente não carregado.')}")
            return

        report_lines = [
            "PATIENT INSPECTOR:"
        ]

        for section_name, section_data in state.items():
            report_lines.append(f"├─ • {section_name}:")
            formatted_content = self._format_compact(section_data, indent=6)
            for line in formatted_content.splitlines():
                report_lines.append(f"│   {line}")

        report_lines.append("└──────────────────────────────────────")

        logger.log(level, "\n" + "\n".join(report_lines))

    # =========================================================================
    # FORMATTING UTILITIES
    # =========================================================================
    @staticmethod
    def _format_compact(data: Any, indent: int = 4) -> str:
        """Formata estruturas de dados de forma minimalista."""
        import pprint
        if not data:
            return "{}"
        return pprint.pformat(
            data,
            indent=indent,
            width=65,
            compact=True,
            sort_dicts=False
        )


__all__ = [
    "Patient_Logger",
]