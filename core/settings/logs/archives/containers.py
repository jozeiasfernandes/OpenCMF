"""Gerenciamento de containers de injeção de dependências e logs da aplicação."""

from typing import Dict, Any, List
from dependency_injector import containers, providers
from core.settings.logs.base_logger import setup_logger

containers_logger_instance = setup_logger("OpenCMF.Containers.Debug", filename=None)


class Containers_logger:
    """Gerencia logs e inspeção do sistema de injeção de dependências."""

    def __init__(self, name: str = "OpenCMF.Containers.Debug"):
        self.logger = setup_logger(name, filename=None)


    # =========================================================================
    # INTERNAL LOGGING HELPER
    # =========================================================================
    def _log_with_context(self, level: str, message: str, exc_info: bool = False, container_name: str = None):
        try:
            prefix = f"[Container: {container_name}] " if container_name else ""
            formatted_msg = f"{prefix}{message}"
            log_method = getattr(self.logger, level.lower(), self.logger.debug)

            if level == "critical":
                log_method(formatted_msg, exc_info=exc_info)
            else:
                log_method(formatted_msg)
        except Exception as e:
            self.logger.error(f"Erro interno no Containers_logger: {e} - Mensagem original: {message}")


    # =========================================================================
    # PUBLIC LOGGING METHODS
    # =========================================================================
    def debug(self, message: str, container_name: str = None):
        self._log_with_context("debug", message, container_name=container_name)

    def info(self, message: str, container_name: str = None):
        self._log_with_context("info", message, container_name=container_name)

    def warning(self, message: str, container_name: str = None):
        self._log_with_context("warning", message, container_name=container_name)

    def error(self, message: str, container_name: str = None):
        self._log_with_context("error", message, container_name=container_name)

    def critical(self, message: str, exc_info: bool = False, container_name: str = None):
        self._log_with_context("critical", message, exc_info=exc_info, container_name=container_name)


    # =========================================================================
    # INSPECTION & REPORTING
    # =========================================================================
    def inspect_container_state(self, container_instance: Any) -> Dict[str, Any]:
        """Inspeciona provedores e estado de um container."""
        info = {}
        try:
            if hasattr(container_instance, "__class__"):
                info["class"] = container_instance.__class__.__name__
            if hasattr(container_instance, "providers"):
                info["providers"] = list(container_instance.providers.keys())
        except Exception as e:
            info["error"] = str(e)
        return info

    def inspect_side_panel_widgets(self, side_panel_widget: Any, container_name: str = "SidePanel"):
        """Inspeciona os widgets filhos do painel lateral."""
        try:
            widgets_info: List[Dict[str, str]] = []
            if hasattr(side_panel_widget, "findChildren"):
                children = side_panel_widget.findChildren(object)
                for child in children:
                    name = child.objectName()
                    text = getattr(child, "text", lambda: "")() if hasattr(child, "text") else ""
                    widgets_info.append({
                        "type": child.__class__.__name__,
                        "name": name or "(sem nome)",
                        "text": text[:30] + ("..." if len(text) > 30 else "") if text else "(vazio)"
                    })

            if not widgets_info:
                self.info("Nenhum widget filho encontrado no Side Panel.", container_name=container_name)
                return []

            report_lines = [
                f"SIDE PANEL: ({len(widgets_info)} elementos) ────────"
            ]
            for idx, w in enumerate(widgets_info):
                report_lines.append(f"├─ [{idx}] Type: {w['type']} | Name: {w['name']} | Text: {w['text']}")
            report_lines.append("└───────────────────────────────────")

            self.info("\n" + "\n".join(report_lines), container_name=container_name)
            return widgets_info
        except Exception as e:
            self.error(f"Erro ao inspecionar side_panel: {e}", container_name=container_name)
            return []


class ApplicationContainer(containers.DeclarativeContainer):
    """Container principal para gerenciamento de dependências."""

    config = providers.Configuration()
    containers_logger = providers.Singleton(Containers_logger)


container = ApplicationContainer()

__all__ = [
    "Containers_logger",
    "containers_logger_instance",
    "ApplicationContainer",
    "container",
]