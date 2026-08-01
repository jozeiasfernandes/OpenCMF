from typing import TYPE_CHECKING
from PySide6 import QtWidgets, QtCore

from core.workspace.models.contracts import IModule
from core.settings.settings_app_manager import settings

if TYPE_CHECKING:
    from core.workspace.containers.toolbar_container.toolbar_manager import ToolbarManager
    from core.workspace.containers.side_panel_container.side_panel_manager import SidePanelManager
    from core.workspace.containers.central_area_container import CentralAreaManager


class ModuleDistributor:

    @staticmethod
    def _is_valid_qwidget(widget) -> bool:
        """Verifica de forma segura se o widget do PySide/C++ ainda existe e não foi deletado."""
        if widget is None:
            return False
        try:
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
        if hasattr(module, "get_toolbar"):
            tb = module.get_toolbar()
            if ModuleDistributor._is_valid_qwidget(tb):
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

                tb.update()
                tb.repaint()

        # 2. Distribuir Side Panels e controlar comportamento do container/splitter
        has_panels = False
        if hasattr(module, "get_side_panel"):
            panels = module.get_side_panel()
            if panels:
                has_panels = True
                for name, widget in panels.items():
                    if ModuleDistributor._is_valid_qwidget(widget):
                        try:
                            widget.setWindowFlags(QtCore.Qt.Widget)
                            if widget.parent():
                                widget.setParent(None)
                        except RuntimeError:
                            continue

                        side_manager.container.add_panel(name, widget)
                        widget.setVisible(True)
                        widget.update()
                        widget.repaint()

        # Identifica o modo atual do side panel ("tabs" ou "floating")
        current_mode = getattr(settings, "side_panel_mode", "tabs")

        if current_mode == "floating":
            floating_win = getattr(side_manager.container, "floating_window", None)
            if floating_win:
                if has_panels:
                    floating_win.show()
                else:
                    floating_win.hide()
        else:
            if hasattr(side_manager, "container") and hasattr(side_manager.container, "parent"):
                splitter = side_manager.container.parent()
                while splitter and not isinstance(splitter, QtWidgets.QSplitter):
                    splitter = splitter.parent()

                if has_panels:
                    side_manager.container.setVisible(True)
                else:
                    side_manager.container.setVisible(False)
                    if splitter:
                        sizes = splitter.sizes()
                        total = sum(sizes)
                        if total > 0:
                            splitter.setSizes([total, 0])

                if splitter:
                    splitter.update()
                    splitter.repaint()

        # 3. Configurar Viewport Central e Ciclo de Vida Unificado
        if hasattr(module, "get_central_area"):
            viewport = module.get_central_area()
            if ModuleDistributor._is_valid_qwidget(viewport):
                if hasattr(viewport, "setup_component") and hasattr(viewport, "_logic"):
                    if hasattr(viewport._logic, "_loaded") and not viewport._logic._loaded:
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

                central_manager.set_view(viewport)

                viewport.setVisible(True)
                viewport.update()
                viewport.repaint()

                if hasattr(central_manager, "get_container"):
                    container = central_manager.get_container()
                    container.update()
                    container.repaint()

    @staticmethod
    def cleanup(
            toolbar_manager: 'ToolbarManager',
            side_manager: 'SidePanelManager',
            central_manager: 'CentralAreaManager'
    ):
        if hasattr(toolbar_manager.top_container, 'toolbars'):
            for tb_id in list(toolbar_manager.top_container.toolbars.keys()):
                toolbar = toolbar_manager.top_container.toolbars.get(tb_id)
                if toolbar:
                    toolbar_manager.top_container.remove_toolbar(tb_id)
                    toolbar.setParent(None)

        if hasattr(side_manager.container, 'clear_all'):
            side_manager.container.clear_all()
            side_manager.container.setVisible(False)

        floating_win = getattr(side_manager.container, "floating_window", None)
        if floating_win:
            floating_win.close()

        if hasattr(central_manager, 'clear'):
            central_manager.clear()