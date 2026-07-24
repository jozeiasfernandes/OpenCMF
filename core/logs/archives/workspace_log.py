import logging
from typing import Dict, Any, List, Optional
from PySide6 import QtWidgets, QtCore

logger = logging.getLogger("OpenCMF.Workspace.Debug")


class Workspace_Logger:
    """
    Classe completa de logs e inspeção para a Workspace do OpenCMF.
    Mapeia a estrutura da workspace, dimensões de containers, dados do paciente,
    módulo ativo, componentes ativos, scene e outras configurações.
    """

    def __init__(self, workspace_manager: QtWidgets.QWidget):
        self.workspace = workspace_manager

    def inspect_full_state(self) -> Dict[str, Any]:
        """Coleta um relatório completo e detalhado do estado atual da workspace."""
        report = {
            "workspace_info": self.get_workspace_dimensions(),
            "patient_data": self.get_patient_data(),
            "active_module": self.get_active_module_info(),
            "components_active": self.get_active_components(),
            "scene_info": self.get_scene_info(),
            "other_configurations": self.get_other_configurations()
        }
        return report

    def log_full_state(self, level: int = logging.INFO) -> None:
        """Gera e registra o relatório completo formatado nos logs da aplicação."""
        state = self.inspect_full_state()

        log_message = (
                "\n" + "=" * 60 + "\n"
                                  "🔍 [WORKSPACE DEBUG INSPECTOR] - RELATÓRIO DE ESTADO\n"
                                  "=" * 60 + "\n"
                                             f"• Dimensões da Workspace & Containers:\n{self._format_dict(state['workspace_info'])}\n"
                                             f"• Dados do Paciente:\n{self._format_dict(state['patient_data'])}\n"
                                             f"• Módulo Ativo:\n{self._format_dict(state['active_module'])}\n"
                                             f"• Componentes Ativos:\n{self._format_dict(state['components_active'])}\n"
                                             f"• Scene / Viewport Central:\n{self._format_dict(state['scene_info'])}\n"
                                             f"• Outras Configurações:\n{self._format_dict(state['other_configurations'])}\n"
                + "=" * 60
        )
        logger.log(level, log_message)

    def get_workspace_dimensions(self) -> Dict[str, Any]:
        """Obtém as dimensões (geometry, largura e altura) de cada container principal."""
        dims = {}

        # Janela principal / WorkspaceManager
        dims["workspace_window"] = {
            "width": self.workspace.width(),
            "height": self.workspace.height(),
            "geometry": self.workspace.geometry().getRect()
        }

        # Header Panel
        if hasattr(self.workspace, "header") and self.workspace.header:
            dims["header_container"] = {
                "width": self.workspace.header.width(),
                "height": self.workspace.header.height(),
                "visible": self.workspace.header.isVisible()
            }

        # Toolbar Manager (Top e Bottom)
        if hasattr(self.workspace, "toolbar_manager") and self.workspace.toolbar_manager:
            dims["toolbar_top"] = {
                "width": self.workspace.toolbar_manager.top_container.width(),
                "height": self.workspace.toolbar_manager.top_container.height(),
                "visible": self.workspace.toolbar_manager.top_container.isVisible()
            }
            dims["toolbar_bottom"] = {
                "width": self.workspace.toolbar_manager.bottom_container.width(),
                "height": self.workspace.toolbar_manager.bottom_container.height(),
                "visible": self.workspace.toolbar_manager.bottom_container.isVisible()
            }

        # Splitter e áreas divididas (Central vs Side Panel)
        if hasattr(self.workspace, "splitter") and self.workspace.splitter:
            dims["splitter_sizes"] = self.workspace.splitter.sizes()

        # Central Area Container
        if hasattr(self.workspace, "central_manager") and self.workspace.central_manager:
            central_cont = self.workspace.central_manager.get_container()
            dims["central_area"] = {
                "width": central_cont.width(),
                "height": central_cont.height(),
                "current_widget": central_cont.currentWidget().__class__.__name__ if central_cont.currentWidget() else None
            }

        # Side Panel Container
        if hasattr(self.workspace, "side_manager") and self.workspace.side_manager:
            side_cont = getattr(self.workspace.side_manager, "container", None)
            if side_cont:
                dims["side_panel"] = {
                    "width": side_cont.width(),
                    "height": side_cont.height(),
                    "visible": side_cont.isVisible(),
                    "mode": getattr(side_cont, "current_mode", "unknown")
                }

        # Status Bar
        if hasattr(self.workspace, "status_bar_manager") and self.workspace.status_bar_manager:
            dims["status_bar"] = {
                "height": self.workspace.status_bar_manager.height(),
                "current_message": self.workspace.status_bar_manager.message_label.text()
            }

        return dims

    def get_patient_data(self) -> Dict[str, Any]:
        """Extrai os dados e o caminho do paciente atualmente vinculado."""
        patient_path = getattr(self.workspace, "current_patient_path", "")
        state_patient = ""

        if hasattr(self.workspace, "state") and hasattr(self.workspace.state, "current_patient"):
            state_patient = self.workspace.state.current_patient

        return {
            "current_patient_path": patient_path,
            "state_patient_path": state_patient,
            "has_patient_loaded": bool(patient_path or state_patient)
        }

    def get_active_module_info(self) -> Dict[str, Any]:
        """Identifica o módulo ativo no momento (via abas ou registro)."""
        active_module = None
        module_id = "Nenhum"
        module_name = "Nenhum"

        if hasattr(self.workspace, "get_modulo_ativo"):
            active_module = self.workspace.get_modulo_ativo()

        if active_module:
            module_id = getattr(active_module, "id", "Desconhecido")
            module_name = getattr(active_module, "nome", "Desconhecido")

        active_registry_list = []
        if hasattr(self.workspace, "registry") and hasattr(self.workspace.registry, "list_active_modules"):
            active_registry_list = self.workspace.registry.list_active_modules()

        return {
            "active_module_id": module_id,
            "active_module_name": module_name,
            "registry_active_modules": active_registry_list
        }

    def get_active_components(self) -> Dict[str, List[str]]:
        """Mapeia todos os componentes ativos nas toolbars, side panels e área central."""
        components = {
            "top_toolbars": [],
            "bottom_toolbars": [],
            "side_panels": [],
            "central_widget": None
        }

        # Toolbars
        if hasattr(self.workspace, "toolbar_manager"):
            if hasattr(self.workspace.toolbar_manager, "top_container"):
                components["top_toolbars"] = list(self.workspace.toolbar_manager.top_container.toolbars.keys())
            if hasattr(self.workspace.toolbar_manager, "bottom_container"):
                components["bottom_toolbars"] = list(self.workspace.toolbar_manager.bottom_container.toolbars.keys())

        # Side Panels
        if hasattr(self.workspace, "side_manager"):
            side_manager = self.workspace.side_manager
            if hasattr(side_manager, "container") and hasattr(side_manager.container, "panels"):
                components["side_panels"] = list(side_manager.container.panels.keys())

        # Central Widget
        if hasattr(self.workspace, "central_manager"):
            central_cont = self.workspace.central_manager.get_container()
            curr_widget = central_cont.currentWidget()
            if curr_widget:
                components["central_widget"] = curr_widget.__class__.__name__

        return components

    def get_scene_info(self) -> Dict[str, Any]:
        """Inspeciona se o widget central possui alguma Scene ativa (ex: VTK, GraphicsView, OpenCascade, etc.)."""
        scene_info = {"has_scene": False, "scene_type": None, "details": {}}

        if not hasattr(self.workspace, "central_manager"):
            return scene_info

        central_cont = self.workspace.central_manager.get_container()
        widget = central_cont.currentWidget()

        if not widget:
            return scene_info

        # Procura recursivamente ou diretamente por atributos comuns de renderização/scene
        target_obj = widget
        if hasattr(widget, "get_scene") and callable(widget.get_scene):
            target_obj = widget.get_scene()
        elif hasattr(widget, "scene") and callable(widget.scene):
            target_obj = widget.scene()
        elif hasattr(widget, "render_window"):
            target_obj = widget.render_window

        if target_obj and target_obj != widget:
            scene_info["has_scene"] = True
            scene_info["scene_type"] = target_obj.__class__.__name__

        # Verificações específicas para QGraphicsScene
        if isinstance(target_obj, QtWidgets.QGraphicsScene):
            scene_info["details"]["items_count"] = len(target_obj.items())

        return scene_info

    def get_other_configurations(self) -> Dict[str, Any]:
        """Coleta configurações globais adicionais do state ou gerenciadores."""
        configs = {}
        if hasattr(self.workspace, "state") and hasattr(self.workspace.state, "get_all_settings"):
            configs = self.workspace.state.get_all_settings()
        return configs

    @staticmethod
    def _format_dict(data: Any, indent: int = 4) -> str:
        """Formata dicionários de forma legível para inserção nos logs."""
        import pprint
        return pprint.pformat(data, indent=indent, width=80, compact=False)