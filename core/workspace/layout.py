from typing import TYPE_CHECKING
from PySide6 import QtWidgets
from .contracts import IModule

if TYPE_CHECKING:
    from .toolbar_container.toolbar_manager import ToolbarManager
    from .side_panel_container.side_panel_manager import SidePanelManager


class ModuleDistributor:
    """
    Responsável por extrair as partes de um módulo e distribuí-las
    para os seus respectivos gerenciadores de interface.
    """

    @staticmethod
    def distribute(
            module: IModule,
            toolbar_manager: 'ToolbarManager',
            side_manager: 'SidePanelManager',
            central_host: QtWidgets.QStackedWidget
    ):
        """
        Extrai os componentes do módulo e registra nos Managers globais.
        """
        # 1. Distribuir Toolbars (se existirem)
        if hasattr(module, "get_workspace_toolbar"):
            tb = module.get_workspace_toolbar()
            if tb:
                # O ID pode vir de uma propriedade do widget ou ser gerado
                tb_id = tb.objectName() or "default_toolbar"
                toolbar_manager.register_toolbar(tb_id, tb)

        # 2. Distribuir Toolboxes (Painéis Laterais)
        if hasattr(module, "get_toolboxes"):
            toolboxes = module.get_toolboxes()
            for name, widget in toolboxes.items():
                side_manager.container.add_panel(name, widget)

        # 3. Configurar Viewport Central
        if hasattr(module, "get_workspace"):
            viewport = module.get_workspace()
            # Remove o widget atual do host se necessário, ou apenas adiciona
            central_host.addWidget(viewport)
            central_host.setCurrentWidget(viewport)

    @staticmethod
    def cleanup(
            toolbar_manager: 'ToolbarManager',
            side_manager: 'SidePanelManager',
            central_host: QtWidgets.QStackedWidget
    ):
        """Limpa todos os containers antes de carregar um novo módulo."""
        # Limpa Toolbars
        for tb_id in list(toolbar_manager.top_container.toolbars.keys()):
            toolbar_manager.top_container.remove_toolbar(tb_id)

        # Limpa Painéis Laterais
        for p_id in list(side_manager.container.panels.keys()):
            side_manager.container.remove_panel(p_id)

        # Limpa Central Host
        while central_host.count() > 0:
            widget = central_host.widget(0)
            central_host.removeWidget(widget)
            widget.deleteLater()