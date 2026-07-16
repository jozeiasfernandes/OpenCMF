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
                tb_id = tb.objectName() or "default_toolbar"
                toolbar_manager.register_toolbar(tb_id, tb)
                tb.setVisible(True)
                tb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        # 2. Distribuir Toolboxes
        if hasattr(module, "get_toolboxes"):
            toolboxes = module.get_toolboxes()
            for name, widget in toolboxes.items():
                side_manager.container.add_panel(name, widget)
                widget.setVisible(True)
                # Garante que o painel lateral seja forçado a mostrar
                side_manager.container.setVisible(True)

        # 3. Configurar Viewport Central
        if hasattr(module, "get_workspace"):
            viewport = module.get_workspace()
            if viewport:
                # Politica essencial para que o widget central não colapse
                viewport.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

                central_host.addWidget(viewport)
                central_host.setCurrentWidget(viewport)

                # FORÇA VISIBILIDADE E ATUALIZAÇÃO
                viewport.setVisible(True)
                viewport.show()

                # NOTIFICA O LAYOUT PAI QUE A ESTRUTURA MUDOU
                if central_host.parent() and central_host.parent().layout():
                    central_host.parent().layout().activate()

                # Força o update do Splitter (quem contém o central_host)
                if hasattr(central_host.parent(), 'splitter'):
                    central_host.parent().splitter.update()

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