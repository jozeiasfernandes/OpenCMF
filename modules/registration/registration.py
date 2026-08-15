from pathlib import Path
from typing import Dict, Optional, Any

from PySide6 import QtWidgets

# Workspace
from core.workspace.modules.base.base_module import ModuleBase

# Scene
from application.scene.scene_manager import SceneManager
from application.scene.scene_state import SceneState
from application.scene.events.event_bus import EventBus
from application.scene.registry.object_registry import ObjectRegistry
from application.scene.registry.actor_registry import ActorRegistry
from application.scene.selection.selection_manager import SelectionManager
from application.scene.io.importer import ObjectImporter
from application.scene.scene_object import SceneObject

# Components
from core.components.bases.base_component import AppContext
from core.components.central_area.viewer_registration_central_area import ViewerRegistration_Widget_CentralArea
from core.components.side_panel.object_manager_sidepanel import ObjectManager_SidePanel
from core.components.side_panel.objetct_properties_sidepanel import ObjectProperties_SidePanel
from core.components.toolbars.registration_toolbar import RegistrationToolbar


# Settings
import logging
logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class RegistrationContext:
    """Wrapper para satisfazer a expectativa do BaseComponent com todos os atributos obrigatórios."""

    def __init__(self, scene_manager, tool_manager=None, event_bus=None):
        self.scene_manager = scene_manager
        self.tool_manager = tool_manager
        self.event_bus = event_bus or getattr(scene_manager, "event_bus", None)


class Modulo(ModuleBase):
    """Módulo de Registro/Alinhamento. Atua como Provedor de Componentes para o ModuleDistributor."""

    def __init__(self, context: Any = None, parent: Optional[QtWidgets.QWidget] = None, **kwargs):
        super().__init__(context=context, parent=parent)

        self.id = "registration"
        self.nome = "Registro"
        self._is_initialized = False

        # Prioriza o scene_manager vindo do contexto ou kwargs, caso contrário cria o padrão
        self.scene_manager = (
                kwargs.get("scene_manager")
                or getattr(context, "scene_manager", None)
                or self._criar_scene_manager_padrao()
        )

        # Extrai opcionalmente o tool_manager do contexto caso exista
        self.tool_manager = kwargs.get("tool_manager") or getattr(context, "tool_manager", None)

        # Cria o objeto de contexto que o BaseComponent espera preenchendo todos os contratos
        self.widget_context = RegistrationContext(
            scene_manager=self.scene_manager,
            tool_manager=self.tool_manager
        )

        # Passa o 'widget_context' para os componentes
        self.widget_reg = ViewerRegistration_Widget_CentralArea(context=self.widget_context)
        self.widget_objetos = ObjectManager_SidePanel(context=self.widget_context)
        self.widget_propriedades = ObjectProperties_SidePanel(context=self.widget_context)

        # Define o volume_viewer principal para a ModuleBase gerenciar
        self.viewer = self.widget_reg

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

    def inicializar(self, path_pacient: str) -> None:
        super().inicializar(path_pacient)
        if self._is_initialized:
            self.cleanup()

        path = Path(path_pacient)
        if not path.exists():
            return

        # Correção: Utiliza o importer existente no scene_manager ou inicializa corretamente
        if hasattr(self.scene_manager, "importer") and self.scene_manager.importer:
            self.object_importer = self.scene_manager.importer
            # Se necessário atualizar o path do paciente no importer
            if hasattr(self.object_importer, "patient_path"):
                self.object_importer.patient_path = path_pacient
        else:
            self.object_importer = ObjectImporter(patient_path=path_pacient)

        if hasattr(self.object_importer, "object_added"):
            self.object_importer.object_added.connect(self._on_scene_object_added)

        self.scene_manager.state.current_patient = path_pacient
        if hasattr(self.widget_objetos, "set_patient_path"):
            self.widget_objetos.set_patient_path(path_pacient)

        self._is_initialized = True
        logger.info(f"Módulo '{self.nome}' inicializado com paciente: {path_pacient}")

    def get_central_area(self) -> QtWidgets.QWidget:
        """Retorna o widget principal da área central do módulo."""
        return self.widget_reg if self.widget_reg is not None else super().get_central_area()

    def get_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        """Retorna a QToolBar seguindo o contrato padrão."""
        manager = tool_manager or self.tool_manager
        context = AppContext(
            tool_manager=manager,
            scene_manager=self.scene_manager,
            settings=getattr(self.context, "settings", None) if self.context else None
        )

        # Armazena como atributo da classe para evitar coleta de lixo prematura pelo Python
        self._registration_toolbar = RegistrationToolbar(
            app_context=context,
            parent=self  # Passa o container/janela atual como parent para manter a árvore de objetos correta
        )

        return self._registration_toolbar

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Objetos": self.widget_objetos,
            "Propriedades": self.widget_propriedades
        }

    def cleanup(self) -> None:
        if self._is_initialized and hasattr(self, 'object_importer'):
            try:
                self.object_importer.object_added.disconnect(self._on_scene_object_added)
            except Exception:
                pass

        for w in [self.widget_reg, self.widget_objetos, self.widget_propriedades]:
            if w:
                try:
                    import shiboken6
                    if shiboken6.isValid(w):
                        w.deleteLater()
                except (RuntimeError, ImportError):
                    pass
                if hasattr(w, "cleanup"):
                    try:
                        w.cleanup()
                    except Exception:
                        pass

        if self.scene_manager:
            try:
                self.scene_manager.clear()
            except Exception:
                pass

        self.widget_reg = None
        self.widget_objetos = None
        self.widget_propriedades = None
        self.viewer = None

        super().cleanup()
        self._is_initialized = False
        logger.info(f"Módulo '{self.nome}' limpo com sucesso.")

    def _on_scene_object_added(self, obj: SceneObject):
        if self.widget_objetos:
            self.widget_objetos.adicionar_objeto_lista(obj.name, obj.type, None, objeto_id=obj.id)


if __name__ == "__main__":
    import sys
    from core.workspace.workspace_manager import WorkspaceManager
    from layout.layout import ModuleDistributor
    from models.module_factory import ModuleFactory

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)


    class MockContext:
        def __init__(self):
            self.app = app
            self.settings = {}


    contexto_mock = MockContext()

    ModuleFactory.register("modulo.registration", Modulo)
    ModuleFactory.set_context(contexto_mock)

    try:
        modulo = ModuleFactory.create("modulo.registration")
        modulo.inicializar("./teste_paciente")

        workspace = WorkspaceManager()
        workspace.resize(1200, 800)

        ModuleDistributor.distribute(
            modulo,
            workspace.toolbar_manager,
            workspace.side_manager,
            workspace.central_manager
        )

        workspace.show()
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Erro fatal ao executar o módulo de registro: {e}", exc_info=True)
        sys.exit(1)