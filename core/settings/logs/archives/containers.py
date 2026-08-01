"""
Módulo de configuração e gerenciamento de containers de injeção de dependências
e serviços da aplicação, incluindo o logger dedicado para containers.
"""

from typing import Dict, Any
from dependency_injector import containers, providers
from settings.logs.base_logger import setup_logger

# Cria o logger específico para o subsistema de containers apenas para o terminal (filename=None)
containers_logger_instance = setup_logger("OpenCMF.Containers.Debug", filename=None)


class Containers_logger:
    """
    Classe dedicada e blindada para gerenciar logs do sistema de containers
    e injeção de dependências, garantindo rastreabilidade de registro e
    imprimindo exclusivamente no terminal.
    """

    def __init__(self, name: str = "OpenCMF.Containers.Debug"):
        # Configura o logger para exibir apenas no terminal (filename=None)
        self.logger = setup_logger(name, filename=None)

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

    def inspect_container_state(self, container_instance: Any) -> Dict[str, Any]:
        """Inspeciona os provedores registrados e o estado atual de um container."""
        info = {
            "container_class": container_instance.__class__.__name__,
            "providers": []
        }
        try:
            if hasattr(container_instance, "providers"):
                info["providers"] = list(container_instance.providers.keys())
        except Exception as e:
            info["inspection_error"] = str(e)
        return info

    def inspect_side_panel_widgets(self, side_panel_widget: Any, container_name: str = "SidePanel"):
        """
        Inspeciona detalhadamente os widgets filhos do painel lateral para diagnosticar duplicações.
        """
        try:
            widgets_info = []
            if hasattr(side_panel_widget, "findChildren"):
                children = side_panel_widget.findChildren(object)
                for child in children:
                    name = child.objectName()
                    text = getattr(child, "text", lambda: "")() if hasattr(child, "text") else ""
                    widgets_info.append({
                        "type": child.__class__.__name__,
                        "name": name,
                        "text": text
                    })

            self.info(f"--- DIAGNÓSTICO DETALHADO DO SIDE PANEL ({len(widgets_info)} elementos) ---",
                      container_name=container_name)
            for idx, w in enumerate(widgets_info):
                self.info(f"[{idx}] Tipo: {w['type']} | ObjectName: '{w['name']}' | Text: '{w['text']}'",
                          container_name=container_name)

            return widgets_info
        except Exception as e:
            self.error(f"Erro ao inspecionar side_panel: {e}", container_name=container_name)
            return []


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Container principal da aplicação para gerenciamento de dependências.
    """

    # Configurações globais opcionais
    config = providers.Configuration()

    # Provedor do logger de containers
    containers_logger = providers.Singleton(
        Containers_logger
    )


# Instância global do container para importação direta nos módulos
container = ApplicationContainer()


__all__ = [
    "Containers_logger",
    "containers_logger_instance",
    "ApplicationContainer",
    "container",
]