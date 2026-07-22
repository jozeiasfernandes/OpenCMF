import logging
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets

logger = logging.getLogger("OpenCMF.Workspace.Loaders")


class WorkspaceComponentHandler:
    """Gerencia a carga, injeção e remoção dinâmica de componentes avulsos vindos da Components_List."""

    def __init__(self, workspace_manager):
        # Usamos weakref ou referência direta para interagir com o workspace e seus managers
        self.workspace = workspace_manager
        self._config_window: Optional[QtWidgets.QWidget] = None

    def abrir_seletor(self):
        """Abre a janela de componentes e conecta o sinal de alteração."""
        if self._config_window is None:
            from core.loaders.components_list import Components_List
            self._config_window = Components_List(self.workspace)
            self._config_window.componente_alterado.connect(self._on_componente_configurado)

        self._config_window.show()
        self._config_window.raise_()
        self._config_window.activateWindow()

    def _on_componente_configurado(self, categoria: str, caminho: Path, ativo: bool):
        """Intercepta a alteração e direciona para o manager correto."""
        modulo_ativo = self.workspace.get_modulo_ativo()
        if not modulo_ativo:
            logger.warning("Tentativa de carregar componente sem módulo ativo.")
            return

        if ativo:
            self._carregar_e_injetar(categoria, caminho, modulo_ativo)
        else:
            self._remover_componente(categoria, caminho)

    def _carregar_e_injetar(self, categoria: str, caminho: Path, modulo_ativo):
        try:
            from core.loaders.loader_components import ComponentLoader

            # Ajustado para corresponder à assinatura do ComponentLoader (caminho, context)
            comp = ComponentLoader.carregar(caminho, modulo_ativo)
            if not comp:
                return

            comp.setProperty("__module_path__", caminho)

            # 1. Toolbars
            if categoria == "toolbars":
                tb_id = comp.objectName() or f"toolbar_{caminho.stem}"
                self.workspace.toolbar_manager.top_container.add_toolbar(tb_id, comp)
                comp.setVisible(True)

            # 2. Side Panels / Toolboxes
            elif categoria in ("side_panel_container", "side_panel_loaders"):
                panel_title = getattr(comp, 'toolbox_name', caminho.stem.replace("_", " ").title())
                panel_id = panel_title.lower().replace(" ", "_")

                side_container = getattr(self.workspace.side_manager, "container", self.workspace.side_manager)
                if hasattr(side_container, "add_panel"):
                    # Passando na ordem correta exigida pelo SidePanelContainer atualizado: panel_id, panel, title
                    side_container.add_panel(panel_id, comp, title=panel_title)
                comp.setVisible(True)

            # 3. Central Area
            elif categoria == "central_area":
                self.workspace.central_manager.set_view(comp)
                comp.setVisible(True)

            logger.info(f"Componente dinâmico '{caminho.name}' carregado na categoria '{categoria}'.")

        except Exception as e:
            logger.error(f"Erro ao carregar componente '{caminho.name}': {e}", exc_info=True)

    def _remover_componente(self, categoria: str, caminho: Path):
        try:
            if categoria == "toolbars":
                tb_id = f"toolbar_{caminho.stem}"
                if hasattr(self.workspace.toolbar_manager.top_container, "remove_toolbar"):
                    self.workspace.toolbar_manager.top_container.remove_toolbar(tb_id)

            elif categoria in ("side_panel_container", "side_panel_loaders"):
                side_container = getattr(self.workspace.side_manager, "container", self.workspace.side_manager)
                if hasattr(side_container, "remover_widget_por_caminho"):
                    side_container.remover_widget_por_caminho(caminho)

            elif categoria == "central_area":
                # Restaura a view padrão do módulo ativo se necessário
                modulo_ativo = self.workspace.get_modulo_ativo()
                if modulo_ativo and hasattr(modulo_ativo, "get_main_widget"):
                    viewport = modulo_ativo.get_main_widget()
                    if viewport:
                        self.workspace.central_manager.set_view(viewport)
                        viewport.setVisible(True)

            logger.info(f"Componente '{caminho.name}' removido da categoria '{categoria}'.")

        except Exception as e:
            logger.error(f"Erro ao remover componente '{caminho.name}': {e}", exc_info=True)