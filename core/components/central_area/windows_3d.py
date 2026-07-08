import os
import sys
import vtk
from PySide6 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from core.scene.rendering.vtk_scene_renderer import VTKSceneRenderer
from core.scene.events.scene_events import SceneEvents
from core.shortcut.shortcuts import get_shortcuts_by_scope


os.environ["QT_API"] = "pyside6"


class Janela3DSurface(QtWidgets.QWidget):
    maximizeRequested = QtCore.Signal(bool)
    objectSelected = QtCore.Signal(str)

    def __init__(self, nome, cor_borda, parent=None, scene_manager=None):
        super().__init__(parent)
        self.nome = nome
        self.cor_borda = cor_borda
        self.scene_manager = scene_manager
        self.is_maximized = False

        self._setup_ui()
        self._setup_vtk()

        if self.scene_manager:
            self.scene_manager.events.subscribe(
                SceneEvents.SELECTION_CHANGED, self._on_selection_changed
            )

        self.shortcuts = get_shortcuts_by_scope("view3d")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def _on_selection_changed(self, selected_ids: list[str]):
        self.render()

    def _setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.setStyleSheet(f"background-color: {self.cor_borda};")

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.main_layout.addWidget(self.vtkWidget)

    def _setup_vtk(self):
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.05, 0.05, 0.05)

        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtkWidget.Initialize()

        self.vtk_scene_renderer = VTKSceneRenderer(self.renderer)

    def _on_left_click(self, obj, event):
        x, y = self.vtkWidget.GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.Pick(x, y, 0, self.renderer)
        actor = picker.GetActor()

        if actor and self.scene_manager:
            pass  # TODO: Implementar lógica de seleção pelo ator

        obj.OnLeftButtonDown()

    def render(self):
        self.vtkWidget.GetRenderWindow().Render()

    def setup_interactors(self):
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()

    def reset_camera(self):
        self.renderer.ResetCamera()
        self.render()


if __name__ == "__main__":
    from core.scene.scene_manager import SceneManager
    from core.scene.scene_state import SceneState
    from core.scene.events.event_bus import EventBus
    from core.scene.registry.object_registry import ObjectRegistry
    from core.scene.registry.actor_registry import ActorRegistry
    from core.scene.selection.selection_manager import SelectionManager
    from core.scene.rendering.vtk_actor_factory import VTKActorFactory
    from core.scene.rendering.scene_bridge import SceneBridge

    app = QtWidgets.QApplication(sys.argv)

    # Preparação das dependências
    event_bus = EventBus()
    state = SceneState()
    object_registry = ObjectRegistry()
    actor_registry = ActorRegistry()
    selection_manager = SelectionManager(state, event_bus)

    # Instanciação do SceneManager
    scene_manager = SceneManager(
        state=state,
        event_bus=event_bus,
        object_registry=object_registry,
        actor_registry=actor_registry,
        selection_manager=selection_manager,
    )

    # Criação da janela
    janela = Janela3DSurface(
        "Vista 3D", "#00AAFF", scene_manager=scene_manager
    )

    # Conexão via Bridge
    bridge = SceneBridge(
        event_bus=event_bus,
        object_registry=object_registry,
        actor_registry=actor_registry,
        renderer=janela.vtk_scene_renderer,
        factory=VTKActorFactory(vtk),
    )

    janela.resize(800, 600)
    janela.show()
    janela.setup_interactors()
    janela.reset_camera()

    sys.exit(app.exec())