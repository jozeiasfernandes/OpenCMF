import logging
from pathlib import Path
from typing import Dict, Optional, Any

from PySide6 import QtWidgets

# Core imports
from core.workspace.contracts import IModule
from core.scene.scene_manager import SceneManager
from core.scene.scene_state import SceneState
from core.scene.events.event_bus import EventBus
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.selection.selection_manager import SelectionManager
from core.scene.io.importer import ObjectImporter
from core.scene.scene_object import SceneObject
from core.scene.events.scene_events import RegistrationEvents

# Components
from core.components.bases.base_toolbar import AppContext
from core.components.central_area.viewer_registration_central_area import ViewerRegistration_Widget_CentralArea
from core.components.side_panel.object_manager_sidepanel import ObjectManager_SidePanel
from core.components.side_panel.objetct_properties_sidepanel import ObjectProperties_SidePanel
from core.components.toolbars.registration_toolbar import RegistrationToolbar

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(IModule):
    """Módulo de Registro/Alinhamento. Atua como Provedor de Componentes para o ModuleDistributor."""

    def __init__(self, **kwargs):
        super().__init__()
        self.id = "modulo.registration"
        self._is_initialized = False
        self._subscribers = []

        self.scene_manager = kwargs.get("scene_manager") or self._criar_scene_manager_padrao()

        self.widget_reg = ViewerRegistration_Widget_CentralArea(context=self.scene_manager)
        self.widget_objetos = ObjectManager_SidePanel(context=self.scene_manager)
        self.widget_propriedades = ObjectProperties_SidePanel(context=self.scene_manager)

        self.widget_reg.setWindowTitle("Registro")
        self.widget_objetos.setWindowTitle("Objetos")
        self.widget_propriedades.setWindowTitle("Propriedades")

    def _criar_scene_manager_padrao(self) -> SceneManager:
        bus = EventBus()
        state = SceneState()
        return SceneManager(
            state=state,
            event_bus=bus,
            object_registry=ObjectRegistry(),
            actor_registry=ActorRegistry(),
            selection_manager=SelectionManager(event_bus=bus, state=state),
            importer=ObjectImporter(patient_path="C:/OpenCMF/data/default_patient"),
            transform_manager=None
        )

    def inicializar(self, caminho_paciente: str) -> None:
        if self._is_initialized:
            self.cleanup()

        path = Path(caminho_paciente)
        if not path.exists():
            return

        self.object_manager = ObjectImporter(patient_path=caminho_paciente)
        self.object_manager.object_added.connect(self._on_scene_object_added)

        self.scene_manager.state.current_patient = caminho_paciente
        if hasattr(self.widget_objetos, "set_patient_path"):
            self.widget_objetos.set_patient_path(caminho_paciente)

        self._is_initialized = True

    def get_main_widget(self) -> QtWidgets.QWidget:
        return self.widget_reg

    def get_workspace_toolbar(self, tool_manager=None) -> Optional[QtWidgets.QToolBar]:
        context = AppContext(
            tool_manager=tool_manager,
            scene_manager=self.scene_manager,
            settings=None
        )

        toolbar = RegistrationToolbar(
            app_context=context,
            parent=None
        )

        toolbar.initialize()

        return toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Objetos": self.widget_objetos,
            "Propriedades": self.widget_propriedades
        }

    def cleanup(self) -> None:
        if not self._is_initialized: return

        if hasattr(self, 'object_manager'):
            try:
                self.object_manager.object_added.disconnect(self._on_scene_object_added)
            except:
                pass

        for w in [self.widget_reg, self.widget_objetos, self.widget_propriedades]:
            if hasattr(w, "cleanup"): w.cleanup()

        self.scene_manager.clear()
        self._is_initialized = False

    def _on_scene_object_added(self, obj: SceneObject):
        self.widget_objetos.adicionar_objeto_lista(obj.name, obj.type, None, objeto_id=obj.id)


if __name__ == "__main__":
    import sys
    from core.workspace.workspace_manager import WorkspaceManager
    from core.workspace.layout import ModuleDistributor
    from core.workspace.module_factory import ModuleFactory

    app = QtWidgets.QApplication(sys.argv)

    # Registra e cria o módulo via Factory
    ModuleFactory.register("modulo.registration", Modulo)
    modulo = ModuleFactory.create("modulo.registration")
    modulo.inicializar("./teste_paciente")

    workspace = WorkspaceManager()

    # O Distributor faz a mágica de injetar o widget, a toolbar e os side panels
    ModuleDistributor.distribute(
        modulo,
        workspace.toolbar_manager,
        workspace.side_manager,
        workspace.central_host
    )

    workspace.show()
    sys.exit(app.exec())