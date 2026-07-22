from typing import TYPE_CHECKING
from PySide6 import QtWidgets, QtCore
from .contracts import IModule

if TYPE_CHECKING:
    from .toolbar_container.toolbar_manager import ToolbarManager
    from .side_panel_container.side_panel_manager import SidePanelManager
    from .central_area_container.central_area_manager import CentralAreaManager


class ModuleDistributor:

    @staticmethod
    def _is_valid_qwidget(widget) -> bool:
        """Verifica de forma segura se o widget do PySide/C++ ainda existe e não foi deletado."""
        if widget is None:
            return False
        try:
            # Tenta acessar uma propriedade simples do C++ para checar se o objeto foi deletado
            _ = widget.metaObject()
            return True
        except RuntimeError:
            return False

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
            if ModuleDistributor._is_valid_qwidget(tb):
                # Garante que a toolbar foi inicializada de forma segura caso venha de implementações legadas
                if hasattr(tb, "initialize") and hasattr(tb, "_is_initialized") and not tb._is_initialized:
                    tb.initialize()

                if not tb.objectName():
                    tb.setObjectName(f"toolbar_{id(tb)}")
                tb_id = tb.objectName()

                toolbar_manager.top_container.add_toolbar(tb_id, tb)

                tb.setVisible(True)
                tb.show()
                for action in tb.actions():
                    action.setVisible(True)

        # 2. Distribuir Toolboxes (Side Panels)
        if hasattr(module, "get_toolboxes"):
            toolboxes = module.get_toolboxes()
            for name, widget in toolboxes.items():
                if ModuleDistributor._is_valid_qwidget(widget):
                    try:
                        widget.setWindowFlags(QtCore.Qt.Widget)
                        if widget.parent():
                            widget.setParent(None)
                    except RuntimeError:
                        continue

                    side_manager.container.add_panel(name, widget)
                    widget.setVisible(True)

        # 3. Configurar Viewport Central
        if hasattr(module, "get_main_widget"):
            viewport = module.get_main_widget()
            if ModuleDistributor._is_valid_qwidget(viewport):
                # Garante que o componente central execute o ciclo de vida padrão do BaseComponent
                if hasattr(viewport, "setup_component") and hasattr(viewport, "_logic"):
                    if not viewport._logic._loaded:
                        viewport.setup_component()

                try:
                    viewport.setWindowFlags(QtCore.Qt.Widget)
                    if viewport.parent():
                        viewport.setParent(None)
                except RuntimeError:
                    pass

                viewport.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Expanding
                )

                # Adicionar ao central_manager
                central_manager.set_view(viewport)

                viewport.setVisible(True)

    @staticmethod
    def cleanup(
            toolbar_manager: 'ToolbarManager',
            side_manager: 'SidePanelManager',
            central_manager: 'CentralAreaManager'
    ):
        if hasattr(toolbar_manager.top_container, 'toolbars'):
            for tb_id in list(toolbar_manager.top_container.toolbars.keys()):
                toolbar_manager.top_container.remove_toolbar(tb_id)

        if hasattr(side_manager.container, 'clear_all'):
            side_manager.container.clear_all()

        if hasattr(central_manager, 'clear'):
            central_manager.clear()