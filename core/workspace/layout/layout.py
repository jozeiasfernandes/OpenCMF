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
        if hasattr(module, "get_workspace_toolbar"):
            tb = module.get_workspace_toolbar()
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

        # 2. Distribuir Toolboxes (Side Panels) e controlar comportamento do container/splitter
        has_toolboxes = False
        if hasattr(module, "get_toolboxes"):
            toolboxes = module.get_toolboxes()
            if toolboxes:
                has_toolboxes = True
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
                        widget.update()
                        widget.repaint()

        # Identifica o modo atual do side panel ("tabs", "toolbox" ou "floating")
        current_mode = getattr(settings, "side_panel_mode", "toolbox")

        if current_mode == "floating":
            # No modo flutuante, a janela flutuante gerencia sua própria visibilidade e componentes
            if side_manager.container and hasattr(side_manager.container, "floating_window"):
                if has_toolboxes:
                    if side_manager.container.floating_window:
                        side_manager.container.floating_window.show()
                else:
                    if side_manager.container.floating_window:
                        side_manager.container.floating_window.hide()
        else:
            # Gerencia a visibilidade e o redimensionamento dinâmico do QSplitter do Side Panel (Modos Tabs e Toolbox)
            if hasattr(side_manager, "container") and hasattr(side_manager.container, "parent"):
                splitter = side_manager.container.parent()
                while splitter and not isinstance(splitter, QtWidgets.QSplitter):
                    splitter = splitter.parent()

                if has_toolboxes:
                    side_manager.container.setVisible(True)
                    if splitter:
                        sizes = splitter.sizes()
                        total = sum(sizes)
                        if total > 0:
                            splitter.setSizes([total - 40, 40])

                            if hasattr(side_manager.container, "header") and hasattr(side_manager.container.header,
                                                                                     "_collapsed"):
                                side_manager.container.header._collapsed = True
                                side_manager.container.header._update_toggle_icon(True)
                                if hasattr(side_manager.container, "content_container"):
                                    side_manager.container.content_container.setVisible(False)
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
        if hasattr(module, "get_main_widget"):
            viewport = module.get_main_widget()
            if ModuleDistributor._is_valid_qwidget(viewport):
                if hasattr(viewport, "setup_component") and hasattr(viewport, "_logic"):
                    if hasattr(viewport._logic, "_loaded") and not viewport._logic._loaded:
                        viewport.setup_component()

                if hasattr(module, "inicializar"):
                    caminho = getattr(module, "current_patient_path", "")
                    try:
                        module.inicializar(caminho)
                    except Exception:
                        pass

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
                toolbar_manager.top_container.remove_toolbar(tb_id)

        if hasattr(side_manager.container, 'clear_all'):
            side_manager.container.clear_all()
            side_manager.container.setVisible(False)

        # Garante o fechamento da janela flutuante se estiver ativa no cleanup
        if hasattr(side_manager.container, 'floating_window') and side_manager.container.floating_window:
            side_manager.container.floating_window.close()
            side_manager.container.floating_window = None

        if hasattr(central_manager, 'clear'):
            central_manager.clear()