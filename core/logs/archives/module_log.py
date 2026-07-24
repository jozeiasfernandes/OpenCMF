import logging
from typing import Dict, Any, List, Optional
from PySide6 import QtWidgets
from core.logs.base_logger import setup_logger

logger = setup_logger("OpenCMF.Module.Debug", filename=None)


class Module_Logger:
    """
    Classe completa de logs e inspeção para Módulos e Fluxos do OpenCMF.
    Mapeia dados do módulo ativo, ferramentas, pré-requisitos, validações,
    além do progresso e etapas de fluxos (FluxoBase).
    """

    def __init__(self, modulo_instance: Optional[Any] = None, fluxo_instance: Optional[Any] = None):
        self.modulo = modulo_instance
        self.fluxo = fluxo_instance

    def inspect_full_state(self) -> Dict[str, Any]:
        """Coleta um relatório completo e detalhado do estado atual do módulo e fluxo."""
        report = {
            "module_info": self.get_module_info(),
            "module_components": self.get_module_components(),
            "module_validations": self.get_module_validations(),
            "fluxo_info": self.get_fluxo_info()
        }
        return report

    def log_full_state(self, level: int = logging.INFO) -> None:
        """Gera e registra o relatório completo formatado em um único bloco nos logs da aplicação."""
        state = self.inspect_full_state()

        report_lines = [
            "=" * 60,
            "🔍 [MODULE & FLUXO DEBUG INSPECTOR] - RELATÓRIO DE ESTADO",
            "=" * 60,
            f"• Informações do Módulo:\n{self._format_dict(state['module_info'])}",
            f"• Componentes & Ferramentas do Módulo:\n{self._format_dict(state['module_components'])}",
            f"• Validações & Pré-requisitos:\n{self._format_dict(state['module_validations'])}",
            f"• Informações do Fluxo:\n{self._format_dict(state['fluxo_info'])}",
            "=" * 60
        ]

        logger.log(level, "\n" + "\n".join(report_lines))

    def get_module_info(self) -> Dict[str, Any]:
        """Obtém as propriedades principais do módulo."""
        if not self.modulo:
            return {"status": "Nenhum módulo vinculado"}

        return {
            "class_name": self.modulo.__class__.__name__,
            "module_id": getattr(self.modulo, "id", "undefined.id"),
            "module_name": getattr(self.modulo, "nome", "Módulo Genérico"),
            "has_viewer": bool(getattr(self.modulo, "viewer", None)),
            "viewer_type": type(self.modulo.viewer).__name__ if getattr(self.modulo, "viewer", None) else None
        }

    def get_module_components(self) -> Dict[str, Any]:
        """Mapeia toolboxes, toolbars e widgets principais do módulo."""
        if not self.modulo:
            return {}

        toolboxes = {}
        try:
            if hasattr(self.modulo, "get_toolboxes") and callable(self.modulo.get_toolboxes):
                tb_dict = self.modulo.get_toolboxes()
                toolboxes = {k: v.__class__.__name__ for k, v in tb_dict.items()}
        except Exception:
            toolboxes = {"error": "Falha ao recuperar toolboxes"}

        main_widget = "Desconhecido"
        try:
            if hasattr(self.modulo, "get_main_widget") and callable(self.modulo.get_main_widget):
                mw = self.modulo.get_main_widget()
                main_widget = mw.__class__.__name__ if mw else None
        except Exception:
            main_widget = "Erro ao recuperar main widget"

        return {
            "toolboxes": toolboxes,
            "main_widget": main_widget
        }

    def get_module_validations(self) -> Dict[str, Any]:
        """Verifica o estado de pré-requisitos e validação de passagem do módulo."""
        if not self.modulo:
            return {}

        pre_req_ok, pre_req_msg = True, ""
        try:
            if hasattr(self.modulo, "verificar_pre_requisitos") and callable(self.modulo.verificar_pre_requisitos):
                pre_req_ok, pre_req_msg = self.modulo.verificar_pre_requisitos()
        except Exception as e:
            pre_req_ok, pre_req_msg = False, str(e)

        valid_pass = True
        try:
            if hasattr(self.modulo, "validar_passagem") and callable(self.modulo.validar_passagem):
                valid_pass = self.modulo.validar_passagem()
        except Exception:
            valid_pass = False

        return {
            "pre_requisitos_ok": pre_req_ok,
            "pre_requisitos_mensagem": pre_req_msg,
            "validar_passagem": valid_pass
        }

    def get_fluxo_info(self) -> Dict[str, Any]:
        """Mapeia o estado atual do fluxo (FluxoBase), etapas e índice."""
        if not self.fluxo:
            return {"status": "Nenhum fluxo vinculado"}

        return {
            "fluxo_nome": getattr(self.fluxo, "nome", "Fluxo Padrão"),
            "total_etapas": getattr(self.fluxo, "total_etapas", 0),
            "indice_atual": getattr(self.fluxo, "indice_atual", 0),
            "id_atual": getattr(self.fluxo, "id_atual", None),
            "sequencia_etapas": getattr(self.fluxo, "sequencia", []),
            "configuracoes": getattr(self.fluxo, "configuracoes", {})
        }

    @staticmethod
    def _format_dict(data: Any, indent: int = 4) -> str:
        """Formata dicionários de forma legível para inserção nos logs."""
        import pprint
        return pprint.pformat(data, indent=indent, width=80, compact=False)