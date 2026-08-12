import logging
from typing import Dict, Any, List
from PySide6 import QtWidgets
from settings.logs.base_logger import setup_logger

# Configura o logger para exibir apenas no terminal (filename=None)
logger = setup_logger("OpenCMF.Workspace.Debug", filename=None)


class Workspace_Logger:
    """
    Classe otimizada de logs e inspeção para a Workspace do OpenCMF.
    Apresenta relatórios limpos, legíveis e minimalistas, ocultando valores vazios ou irrelevantes.
    """

    def __init__(self, workspace_manager: QtWidgets.QWidget):
        self.workspace = workspace_manager

    # =========================================================================
    # INSPECTION & REPORTING
    # =========================================================================
    def inspect_full_state(self) -> Dict[str, Any]:
        """Coleta o estado completo filtrando dados vazios para manter o log enxuto."""
        report = {}

        dims = self.get_workspace_dimensions()
        if dims:
            report["Dimensões & Containers"] = dims

        patient = self.get_patient_data()
        if patient.get("has_patient_loaded"):
            report["Paciente"] = patient

        module = self.get_active_module_info()
        if module.get("active_module_name") != "Nenhum" or module.get("registry_active_modules"):
            report["Módulo Ativo"] = module

        components = self.get_active_components()
        if any(components.values()):
            report["Componentes Ativos"] = components

        scene = self.get_scene_info()
        if scene.get("has_scene"):
            report["Scene / Viewport"] = scene

        configs = self.get_other_configurations()
        if configs:
            report["Configurações"] = configs

        return report

    def log_full_state(self, level: int = logging.INFO) -> None:
        """Gera um relatório estruturado e minimalista, exibindo apenas seções ativas."""
        state = self.inspect_full_state()

        if not state:
            logger.log(level, "[WORKSPACE] Estado vazio ou workspace não inicializada.")
            return

        report_lines = [
            "WORKSPACE:"
        ]

        for section_name, section_data in state.items():
            report_lines.append(f"├─ • {section_name}:")
            formatted_content = self._format_compact(section_data, indent=6)
            for line in formatted_content.splitlines():
                report_lines.append(f"│   {line}")

        report_lines.append("└───────────────────────────────────────────────")

        logger.log(level, "\n" + "\n".join(report_lines))

    # =========================================================================
    # STATE GATHERING HELPERS
    # =========================================================================
    def get_workspace_dimensions(self) -> Dict[str, Any]:
        """Obtém as dimensões resumidas dos containers ativos."""
        dims = {}

        if hasattr(self.workspace, "width"):
            dims["window"] = f"{self.workspace.width()}x{self.workspace.height()}"

        if hasattr(self.workspace, "splitter") and self.workspace.splitter:
            dims["splitter"] = self.workspace.splitter.sizes()

        if hasattr(self.workspace, "central_manager") and self.workspace.central_manager:
            central_cont = self.workspace.central_manager.get_container()
            if central_cont and central_cont.currentWidget():
                dims["central_widget"] = central_cont.currentWidget().__class__.__name__

        return dims

    def get_patient_data(self) -> Dict[str, Any]:
        """Extrai os dados e o caminho do paciente atualmente vinculado."""
        patient_path = getattr(self.workspace, "current_patient_path", "")
        state_patient = ""

        if hasattr(self.workspace, "state") and hasattr(self.workspace.state, "current_patient"):
            state_patient = self.workspace.state.current_patient

        return {
            "path": patient_path or state_patient,
            "has_patient_loaded": bool(patient_path or state_patient)
        }

    def get_active_module_info(self) -> Dict[str, Any]:
        """Identifica o módulo ativo no momento."""
        active_module = None
        module_name = "Nenhum"

        if hasattr(self.workspace, "get_modulo_ativo"):
            active_module = self.workspace.get_modulo_ativo()

        if active_module:
            module_name = getattr(active_module, "nome", "Desconhecido")

        return {
            "active_module_name": module_name,
            "registry_active_modules": getattr(self.workspace, "registry", None) and getattr(self.workspace.registry, "list_active_modules", lambda: [])()
        }

    def get_active_components(self) -> Dict[str, List[str]]:
        """Mapeia componentes ativos de forma concisa."""
        components = {}

        if hasattr(self.workspace, "toolbar_manager"):
            tm = self.workspace.toolbar_manager
            if hasattr(tm, "top_container") and tm.top_container.toolbars:
                components["top_toolbars"] = list(tm.top_container.toolbars.keys())
            if hasattr(tm, "bottom_container") and tm.bottom_container.toolbars:
                components["bottom_toolbars"] = list(tm.bottom_container.toolbars.keys())

        if hasattr(self.workspace, "side_manager"):
            sm = self.workspace.side_manager
            if hasattr(sm, "container") and hasattr(sm.container, "panels"):
                components["side_panels"] = list(sm.container.panels.keys())

        return {k: v for k, v in components.items() if v}

    def get_scene_info(self) -> Dict[str, Any]:
        """Inspeciona o estado da cena atual se disponível."""
        scene_info = {"has_scene": False}

        if not hasattr(self.workspace, "central_manager"):
            return scene_info

        central_cont = self.workspace.central_manager.get_container()
        widget = central_cont.currentWidget() if central_cont else None

        if not widget:
            return scene_info

        target_obj = widget
        if hasattr(widget, "get_scene") and callable(widget.get_scene):
            target_obj = widget.get_scene()
        elif hasattr(widget, "render_window"):
            target_obj = widget.render_window

        if target_obj and target_obj != widget:
            scene_info["has_scene"] = True
            scene_info["type"] = target_obj.__class__.__name__

        return scene_info

    def get_other_configurations(self) -> Dict[str, Any]:
        """Coleta configurações adicionais se existentes."""
        if hasattr(self.workspace, "state") and hasattr(self.workspace.state, "get_all_settings"):
            return self.workspace.state.get_all_settings() or {}
        return {}

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