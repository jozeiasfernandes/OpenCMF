# core/workspace/layout.py

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
        # 1. Distribuir Toolbars
        if hasattr(module, "get_workspace_toolbar"):
            tb = module.get_workspace_toolbar()
            if tb:
                tb_id = tb.objectName() or f"toolbar_{id(tb)}"
                # Garantir que a toolbar seja adicionada ao container correto
                toolbar_manager.top_container.add_toolbar(tb_id, tb)
                tb.setVisible(True)

        # 2. Distribuir Toolboxes (Side Panels)
        if hasattr(module, "get_toolboxes"):
            toolboxes = module.get_toolboxes()
            for name, widget in toolboxes.items():
                if widget:
                    # IMPORTANTE: Remover o widget de qualquer parent anterior
                    if widget.parent():
                        widget.setParent(None)

                    # Adicionar ao container lateral
                    side_manager.container.add_panel(name, widget)
                    widget.setVisible(True)

        # 3. Configurar Viewport Central
        if hasattr(module, "get_main_widget"):
            viewport = module.get_main_widget()
            if viewport:
                # Remover de qualquer parent anterior
                if viewport.parent():
                    viewport.setParent(None)

                # Garantir políticas de tamanho
                viewport.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Expanding
                )

                # Adicionar ao central_host
                central_host.addWidget(viewport)
                central_host.setCurrentWidget(viewport)
                viewport.setVisible(True)

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
        if hasattr(side_manager.container, 'panels'):
            for p_id in list(side_manager.container.panels.keys()):
                side_manager.container.remove_panel(p_id)

        # Limpa Central Host
        while central_host.count() > 0:
            widget = central_host.widget(0)
            central_host.removeWidget(widget)
            widget.deleteLater()