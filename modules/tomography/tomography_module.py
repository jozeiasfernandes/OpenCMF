from __future__ import annotations

import sys
import os
import logging
from typing import Dict, Optional, Any
from PySide6 import QtWidgets, QtCore

# Scene
from application.scene.events.event_bus import EventBus
from application.scene.registry.actor_registry import ActorRegistry

# Module
from core.workspace.modules.base.base_module import ModuleBase
from modules.tomography.ui.tomography_components import TomographyComponents
from modules.tomography.logic.tomography_controller import TomographyController
from modules.tomography.logic.tomography_signals_events import TomographySignals

# Logs
logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Module(ModuleBase):
    id = "tomography"
    name = "Tomografia"

    def __init__(self, context: Any, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, parent=parent)

        self.project_service = getattr(context, "project_service", None)
        self.scene_manager = getattr(context, "scene_manager", None)
        self.object_registry = getattr(context, "object_registry", None)

        self.app_context = context
        self.signals = TomographySignals()

        # Instancia as camadas de componentes e controlador
        self.components = TomographyComponents(context=context, controller=self)
        self.controller = TomographyController(module_instance=self)

        if self.event_bus and hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("DICOM_LOADED", self.controller.handle_dicom_loaded_event)
            logger.info("[Module Tomografia] Inscrito com sucesso no evento 'DICOM_LOADED'.")
        else:
            logger.warning(
                "[Module Tomografia] event_bus não está disponível ou não possui método 'subscribe' no __init__!")

    # =========================================================================
    # COMPONENTS
    # =========================================================================
    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        return self.components.get_workspace_toolbar(tool_manager=tool_manager)

    def get_central_area(self) -> QtWidgets.QWidget:
        return self.components.get_central_area()

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        return self.components.get_side_panel()

    # =========================================================================
    # LIFECYCLE & CONFIGURATION
    # =========================================================================
    def configure_resources(self, caminho_paciente: str) -> None:
        """Método chamado pelo ModuleBase.inicializar() do Workspace."""
        logger.info(f"[Module Tomografia] Configurando recursos para o paciente: {caminho_paciente}")
        self.controller.load_project_configs(caminho_paciente)

        if self.controller.caminho_dicom:
            self.controller.validate_dicom()

    def cleanup(self) -> None:
        if self.event_bus and hasattr(self.event_bus, "unsubscribe"):
            try:
                self.event_bus.unsubscribe("DICOM_LOADED", self.controller.handle_dicom_loaded_event)
                logger.info("[Module Tomografia] Desinscrito do evento 'DICOM_LOADED'.")
            except Exception:
                pass

        if self.controller:
            self.controller.cleanup()

        if self.components:
            self.components.cleanup()

        logger.info(f"Cleanup do módulo {self.name} executado com sucesso.")


if __name__ == "__main__":
    from PySide6.QtCore import QEvent
    from core.components.bases.base_component import AppContext


    class DebugEventFilter(QtCore.QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.MouseButtonPress:
                print(f"[DEBUG CLIQUE] Mouse pressionado em: {obj}")
            return super().eventFilter(obj, event)


    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    filter_inst = DebugEventFilter()
    app.installEventFilter(filter_inst)

    path_teste = os.path.abspath("../debug_paciente")
    os.makedirs(os.path.join(path_teste, "projeto"), exist_ok=True)


    class InteractiveMockToolManager:
        def __init__(self, context_ref):
            self.tools = {}
            self.active_tool = None
            self.context_ref = context_ref

        def get_tool(self, key):
            return self.tools.get(key)

        def register_tool(self, *args):
            if len(args) == 2:
                self.tools[args[0]] = args[1]
            elif len(args) == 1 and hasattr(args[0], "name"):
                self.tools[args[0].name] = args[0]

        def activate_tool(self, tool):
            self.active_tool = tool
            if hasattr(tool, "on_activate"):
                tool.on_activate()


    class MockSettings:
        def get(self, key, default=None): return default

        def set(self, key, value): pass


    event_bus_inst = EventBus()

    contexto_mock = AppContext(
        tool_manager=None,
        scene_manager=None,
        settings=MockSettings(),
        event_bus=event_bus_inst
    )

    tool_manager_mock = InteractiveMockToolManager(contexto_mock)
    contexto_mock.tool_manager = tool_manager_mock

    setattr(contexto_mock, "object_registry", ActorRegistry())
    setattr(contexto_mock, "project_service", None)

    modulo = Modulo(context=contexto_mock)
    modulo.initialize(path_teste)

    janela_teste = QtWidgets.QMainWindow()
    janela_teste.setWindowTitle(f"Debug Mode Interativo: {modulo.name}")
    janela_teste.resize(1200, 800)

    toolbar = modulo.get_workspace_toolbar(tool_manager=tool_manager_mock)
    if toolbar:
        janela_teste.addToolBar(toolbar)

    janela_teste.setCentralWidget(modulo.get_central_area())
    janela_teste.show()

    try:
        sys.exit(app.exec())
    finally:
        modulo.cleanup()