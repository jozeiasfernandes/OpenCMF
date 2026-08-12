from typing import Any, Optional
from settings.logs.base_logger import setup_logger

themes_logger = setup_logger("opencmf.themes", filename=None)


class Themes_Logger:
    """
    Classe dedicada para gerenciar logs, debugs e monitoramento do subsistema de temas,
    garantindo rastreabilidade das operações e emitindo as mensagens no terminal e na UI.
    """

    _instance = None

    def __init__(self, name: str = "opencmf.themes"):
        self.logger = setup_logger(name, filename=None)
        self._theme_context: Optional[Any] = None

    @classmethod
    def get_instance(cls) -> "Themes_Logger":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_context(self, theme_manager: Any):
        """Define o contexto do ThemeManager para extração de dados em tempo de execução."""
        self._theme_context = theme_manager

    # =========================================================================
    # LOGGING METHODS
    # =========================================================================
    def debug(self, message: str, theme_name: str = None):
        self._log_with_context("debug", message, theme_name=theme_name)

    def info(self, message: str, theme_name: str = None):
        self._log_with_context("info", message, theme_name=theme_name)

    def warning(self, message: str, theme_name: str = None):
        self._log_with_context("warning", message, theme_name=theme_name)

    def error(self, message: str, theme_name: str = None, exc_info: bool = False):
        self._log_with_context("error", message, theme_name=theme_name, exc_info=exc_info)

    def _log_with_context(self, level: str, message: str, theme_name: str = None, exc_info: bool = False):
        try:
            prefix = f"[Theme: {theme_name}] " if theme_name else "[ThemeManager] "
            formatted_msg = f"{prefix}{message}"
            log_method = getattr(self.logger, level.lower(), self.logger.debug)

            if level == "error" and exc_info:
                log_method(formatted_msg, exc_info=True)
            else:
                log_method(formatted_msg)
        except Exception as e:
            self.logger.error(f"Erro interno no Themes_Logger: {e} - Mensagem original: {message}")

    # =========================================================================
    # INSPECTION & REPORTING
    # =========================================================================
    def inspect_theme_state(self) -> dict:
        """Extrai informações consolidadas do estado atual do gerenciador de temas."""
        info = {
            "has_context": self._theme_context is not None,
            "customizations": {}
        }

        if not self._theme_context:
            return info

        ctx = self._theme_context

        try:
            if hasattr(ctx, "get_user_customizations"):
                info["customizations"] = ctx.get_user_customizations()
        except Exception as e:
            self.logger.error(f"Erro ao inspecionar o estado do tema: {e}")

        return info

    def log_full_state(self):
        """Gera e registra um relatório completo estruturado do tema atual."""
        state = self.inspect_theme_state()

        import pprint
        formatted_state = pprint.pformat(state, indent=4, width=70, sort_dicts=False)

        report_lines = [
            "=" * 60,
            "🎨 [THEMES DEBUG INSPECTOR] - RELATÓRIO DE ESTADO",
            "=" * 60,
            f"{formatted_state}",
            "=" * 60
        ]

        self.logger.info("\n" + "\n".join(report_lines))


# Instância global para importação direta
themes_logger_instance = Themes_Logger.get_instance()

__all__ = [
    "Themes_Logger",
    "themes_logger",
    "themes_logger_instance",
]