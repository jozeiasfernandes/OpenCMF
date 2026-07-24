import logging
import sys
from typing import Any, Optional
from core.logs.base_logger import setup_logger

# Cria o logger específico para o sistema principal apenas para o terminal (filename=None)
main_logger = setup_logger("OpenCMF.Main", filename=None)


class Main_Logger:
    """Classe responsável por gerenciar logs, debugs, interceptar o print()
    e enriquecer os registros com dados do contexto, paciente, cena e workspace,
    emitindo as mensagens exclusivamente no terminal.
    """

    _instance = None

    def __init__(self, name: str = "OpenCMF.Stdout"):
        # Configura o logger para exibir apenas no terminal (filename=None)
        self.logger = setup_logger(name, filename=None)
        self.terminal = sys.stdout  # Mantém a referência original caso precise
        self._application_context: Optional[Any] = None

    @classmethod
    def setup_redirect(cls):
        """Substitui o sys.stdout global para capturar todas as chamadas de print()."""
        if cls._instance is None:
            cls._instance = cls()
            sys.stdout = cls._instance
        return cls._instance

    @classmethod
    def get_instance(cls) -> Optional["Main_Logger"]:
        return cls._instance

    def set_context(self, context: Any):
        """Define o contexto global da aplicação para extração de dados em tempo de execução."""
        self._application_context = context

    def write(self, message: str):
        """Intercepta o que seria enviado para o print() e envia para o logger."""
        message = message.strip()
        if message:  # Evita registrar linhas em branco geradas por prints vazios
            self.logger.debug(message)

    def flush(self):
        """Necessário para manter compatibilidade com o buffer do sys.stdout."""
        pass

    def log_system_state(self, message: str, level: str = "info"):
        """Registra uma mensagem enriquecida com metadados do estado atual da aplicação."""
        state_data = self.get_current_state_info()
        enriched_message = f"{message} | System State: {state_data}"

        log_method = getattr(self.logger, level.lower(), self.logger.debug)
        log_method(enriched_message)

    def get_current_state_info(self) -> dict:
        """Extrai informações consolidadas do estado do paciente, cena e workspace."""
        info = {
            "patient_path": None,
            "scene_state": None,
            "active_module": None,
            "registered_objects_count": 0,
            "actors_count": 0
        }

        if not self._application_context:
            return info

        ctx = self._application_context

        # Extrai caminho do paciente do ProjectService ou Workspace
        try:
            if hasattr(ctx, "workspace_manager") and ctx.workspace_manager:
                if hasattr(ctx.workspace_manager, "current_patient_path"):
                    info["patient_path"] = ctx.workspace_manager.current_patient_path
        except Exception:
            pass

        # Extrai dados do SceneManager e Registries
        try:
            if hasattr(ctx, "scene_manager") and ctx.scene_manager:
                if hasattr(ctx.scene_manager, "state"):
                    info["scene_state"] = str(ctx.scene_manager.state)

            if hasattr(ctx, "object_registry") and ctx.object_registry:
                if hasattr(ctx.object_registry, "get_all"):
                    info["registered_objects_count"] = len(ctx.object_registry.get_all())

            if hasattr(ctx, "actor_registry") and ctx.actor_registry:
                if hasattr(ctx.actor_registry, "get_all"):
                    info["actors_count"] = len(ctx.actor_registry.get_all())
        except Exception:
            pass

        # Extrai dados do Workspace / Módulo Ativo
        try:
            if hasattr(ctx, "workspace_manager") and ctx.workspace_manager:
                if hasattr(ctx.workspace_manager, "get_modulo_ativo"):
                    active_mod = ctx.workspace_manager.get_modulo_ativo()
                    if active_mod:
                        info["active_module"] = getattr(active_mod, "nome", type(active_mod).__name__)
        except Exception:
            pass

        return info


__all__ = [
    "Main_Logger",
    "main_logger",
]