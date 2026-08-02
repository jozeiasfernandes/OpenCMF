import sys
from typing import Any, Optional
from settings.logs.base_logger import setup_logger

scene_logger = setup_logger("OpenCMF.Scene.Debug", filename=None)


class Scene_Logger:
    """
    Classe dedicada para gerenciar logs, debugs e monitoramento do subsistema de cena,
    garantindo rastreabilidade das operações e emitindo as mensagens exclusivamente no terminal.
    """

    _instance = None

    def __init__(self, name: str = "OpenCMF.Scene.Debug"):
        self.logger = setup_logger(name, filename=None)
        self._scene_context: Optional[Any] = None

    @classmethod
    def get_instance(cls) -> "Scene_Logger":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_context(self, scene_manager: Any):
        """Define o contexto do SceneManager para extração de dados em tempo de execução."""
        self._scene_context = scene_manager

    def debug(self, message: str, object_id: str = None):
        self._log_with_context("debug", message, object_id=object_id)

    def info(self, message: str, object_id: str = None):
        self._log_with_context("info", message, object_id=object_id)

    def warning(self, message: str, object_id: str = None):
        self._log_with_context("warning", message, object_id=object_id)

    def error(self, message: str, object_id: str = None, exc_info: bool = False):
        self._log_with_context("error", message, object_id=object_id, exc_info=exc_info)

    def _log_with_context(self, level: str, message: str, object_id: str = None, exc_info: bool = False):
        try:
            prefix = f"[Scene Object: {object_id}] " if object_id else "[Scene] "
            formatted_msg = f"{prefix}{message}"
            log_method = getattr(self.logger, level.lower(), self.logger.debug)

            if level == "error" and exc_info:
                log_method(formatted_msg, exc_info=True)
            else:
                log_method(formatted_msg)
        except Exception as e:
            self.logger.error(f"Erro interno no Scene_Logger: {e} - Mensagem original: {message}")

    def inspect_scene_state(self) -> dict:
        """Extrai informações consolidadas do estado atual da cena e de seus componentes."""
        info = {
            "objects_count": 0,
            "actors_count": 0,
            "selected_objects": [],
            "scene_state_details": {}
        }

        if not self._scene_context:
            return info

        ctx = self._scene_context

        try:
            if hasattr(ctx, "objects") and hasattr(ctx.objects, "count"):
                info["objects_count"] = ctx.objects.count()

            if hasattr(ctx, "actors") and hasattr(ctx.actors, "_actors"):
                info["actors_count"] = len(ctx.actors._actors)

            if hasattr(ctx, "selection") and hasattr(ctx.selection, "selected_ids"):
                info["selected_objects"] = ctx.selection.selected_ids

            if hasattr(ctx, "state") and ctx.state:
                info["scene_state_details"] = {
                    "active_viewer": getattr(ctx.state, "active_viewer", None),
                    "current_patient": getattr(ctx.state, "current_patient", None),
                    "active_tool_name": getattr(ctx.state, "active_tool_name", None)
                }
        except Exception as e:
            self.logger.error(f"Erro ao inspecionar o estado da cena: {e}")

        return info

    def log_full_state(self):
        """Gera e registra um relatório completo estruturado da cena atual."""
        state = self.inspect_scene_state()

        import pprint
        formatted_state = pprint.pformat(state, indent=4, width=70, sort_dicts=False)

        report_lines = [
            "=" * 60,
            "🔍 [SCENE DEBUG INSPECTOR] - RELATÓRIO DE ESTADO",
            "=" * 60,
            f"{formatted_state}",
            "=" * 60
        ]

        self.logger.info("\n" + "\n".join(report_lines))


# Instância global para importação direta
scene_logger_instance = Scene_Logger.get_instance()

__all__ = [
    "Scene_Logger",
    "scene_logger",
    "scene_logger_instance",
]