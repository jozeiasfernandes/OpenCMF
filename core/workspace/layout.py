# core/workspace/layout.py

from typing import TYPE_CHECKING
from PySide6 import QtWidgets, QtCore
from .contracts import IModule

if TYPE_CHECKING:
    from .toolbar_container.toolbar_manager import ToolbarManager
    from .side_panel_container.side_panel_manager import SidePanelManager
    from .central_area_container.central_area_manager import CentralAreaManager


class ModuleDistributor:

    @staticmethod
    def distribute(
            module: IModule,
            toolbar_manager: 'ToolbarManager',
            side_manager: 'SidePanelManager',
            central_manager: 'CentralAreaManager'
    ):
        # 1. Distribuir Toolbars
        if hasattr(module, "get_workspace_toolbar"):
            tb = module.get_workspace_toolbar()
            if tb:
                tb_id = tb.objectName() or f"toolbar_{id(tb)}"
                toolbar_manager.top_container.add_toolbar(tb_id, tb)
                tb.setVisible(True)

        # 2. Distribuir Toolboxes (Side Panels)
        if hasattr(module, "get_toolboxes"):
            toolboxes = module.get_toolboxes()
            for name, widget in toolboxes.items():
                if widget:
                    widget.setWindowFlags(QtCore.Qt.Widget)
                    if widget.parent():
                        widget.setParent(None)

                    side_manager.container.add_panel(name, widget)
                    widget.setVisible(True)

        # 3. Configurar Viewport Central
        if hasattr(module, "get_main_widget"):
            viewport = module.get_main_widget()
            if viewport:
                viewport.setWindowFlags(QtCore.Qt.Widget)
                if viewport.parent():
                    viewport.setParent(None)

                viewport.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Expanding
                )

                # Adicionar ao central_manager
                central_manager.set_view(viewport)

                # Garantir visibilidade
                viewport.setVisible(True)

    @staticmethod
    def cleanup(
            toolbar_manager: 'ToolbarManager',
            side_manager: 'SidePanelManager',
            central_manager: 'CentralAreaManager'
    ):

        for tb_id in list(toolbar_manager.top_container.toolbars.keys()):
            toolbar_manager.top_container.remove_toolbar(tb_id)

        if hasattr(side_manager.container, 'panels'):
            for p_id in list(side_manager.container.panels.keys()):
                side_manager.container.remove_panel(p_id)

        central_manager.clear()