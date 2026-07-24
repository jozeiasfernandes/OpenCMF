import logging
from pathlib import Path
from core.logs.base_logger import setup_logger

home_page_logger = setup_logger("OpenCMF.HomePage", filename=None)


class HomePageDebugLogger:
    """Classe dedicada e blindada para gerenciar logs da home page,
    garantindo que caminhos e dados do paciente apareçam sem exceções silenciosas
    e imprimindo exclusivamente no terminal.
    """

    def __init__(self, name: str = "OpenCMF.HomePage.Debug"):
        # Configura o logger para exibir apenas no terminal (filename=None)
        self.logger = setup_logger(name, filename=None)

    def debug(self, message: str, patient_path: str = None):
        self._log_with_context("debug", message, patient_path=patient_path)

    def info(self, message: str, patient_path: str = None):
        self._log_with_context("info", message, patient_path=patient_path)

    def warning(self, message: str, patient_path: str = None):
        self._log_with_context("warning", message, patient_path=patient_path)

    def error(self, message: str, patient_path: str = None):
        self._log_with_context("error", message, patient_path=patient_path)

    def critical(self, message: str, exc_info: bool = False, patient_path: str = None):
        self._log_with_context("critical", message, exc_info=exc_info, patient_path=patient_path)

    def _log_with_context(self, level: str, message: str, exc_info: bool = False, patient_path: str = None):
        try:
            context_data = self._extract_patient_info(patient_path)
            prefix = ""
            if context_data:
                prefix = f"[Patient: {context_data.get('patient_name', 'Desconhecido')} | Path: {context_data.get('path', 'N/A')}] "
            elif patient_path:
                prefix = f"[Path: {patient_path}] "

            formatted_msg = f"{prefix}{message}"
            log_method = getattr(self.logger, level.lower(), self.logger.debug)

            if level == "critical":
                log_method(formatted_msg, exc_info=exc_info)
            else:
                log_method(formatted_msg)
        except Exception as e:
            self.logger.error(f"Erro interno no HomePageDebugLogger: {e} - Mensagem original: {message}")

    def _extract_patient_info(self, patient_path: str = None) -> dict:
        info = {}
        if not patient_path:
            return info

        try:
            path_obj = Path(patient_path)
            info["path"] = str(path_obj.resolve())
            info["folder_name"] = path_obj.name

            meta_file = path_obj / "metadata.json"
            if not meta_file.exists():
                json_files = list(path_obj.glob("*.json"))
                if json_files:
                    meta_file = json_files[0]

            if meta_file and meta_file.exists():
                import json
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "paciente" in data and isinstance(data["paciente"], dict):
                        info["patient_name"] = data["paciente"].get("nome", "Desconhecido")
                        info["patient_id"] = data["paciente"].get("id", "N/A")
                    elif "name" in data:
                        info["patient_name"] = data.get("name")
            else:
                info["patient_name"] = path_obj.name

        except Exception as e:
            info["extraction_error"] = str(e)

        return info


__all__ = [
    "HomePageDebugLogger",
    "home_page_logger",
]