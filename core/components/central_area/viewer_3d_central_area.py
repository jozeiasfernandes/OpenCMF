import os
import sys
import vtk
from PySide6 import QtCore, QtWidgets

from application.scene.rendering.vtk_scene_renderer import VTKSceneRenderer
from application.scene.events.scene_events import SceneEvents
from settings.shortcuts.shortcut_manager import get_shortcuts_by_scope
from core.components.bases.base_central_area import CentralAreaBase

os.environ["QT_API"] = "pyside6"


class Viewer3D_Widget_CentralArea(CentralAreaBase):
    maximizeRequested = QtCore.Signal(bool)
    objectSelected = QtCore.Signal(str)

    def __init__(self, context, nome="Vista 3D", cor_borda="#00AAFF", parent=None):
        super().__init__(context=context, title=nome, cor_identificacao=cor_borda, usar_vtk=True, parent=parent)
        self.nome = nome
        self.cor_borda = cor_borda
        self.is_maximized = False

        self._setup_specific_ui()
        self._setup_vtk_scene()

        if self.scene_manager and hasattr(self.scene_manager, "events") and self.scene_manager.events:
            self.scene_manager.events.subscribe(
                SceneEvents.SELECTION_CHANGED, self._on_selection_changed
            )

        self.shortcuts = get_shortcuts_by_scope("view3d")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        if self.vtkWidget:
            self.vtkWidget.installEventFilter(self)

    def eventFilter(self, source, event):
        if source is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() == QtCore.Qt.LeftButton:
                self._toggle_maximize()
                return True
        return super().eventFilter(source, event)

    def _on_selection_changed(self, selected_ids: list[str]):
        self.render()

    def _setup_specific_ui(self):
        self.setStyleSheet(f"background-colors: {self.cor_borda};")

        self.btn_maximize = QtWidgets.QPushButton()
        self.btn_maximize.setFixedSize(24, 24)
        self.btn_maximize.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_maximize.clicked.connect(self._toggle_maximize)
        self._update_maximize_icon()

        self.adicionar_controle(self.btn_maximize)

    def _setup_vtk_scene(self):
        if self.renderer:
            self.renderer.SetBackground(0.05, 0.05, 0.05)
            self.vtk_scene_renderer = VTKSceneRenderer(self.renderer)

    def _toggle_maximize(self):
        self.is_maximized = not self.is_maximized
        self._update_maximize_icon()
        self.maximizeRequested.emit(self.is_maximized)

    def _update_maximize_icon(self):
        self.btn_maximize.setText("🗖" if not self.is_maximized else "🗗")
        self.btn_maximize.setStyleSheet("""
            QPushButton { border: none; background: transparent; colors: white; font-weight: bold; } 
            QPushButton:hover { background: #444; border-radius: 3px; }
        """)

    def _on_left_click(self, obj, event):
        if self.vtkWidget:
            x, y = self.vtkWidget.GetEventPosition()
            picker = vtk.vtkPropPicker()
            picker.Pick(x, y, 0, self.renderer)
            actor = picker.GetActor()

            if actor and self.scene_manager:
                pass  # TODO: Implementar lógica de seleção pelo ator

        obj.OnLeftButtonDown()

    def setup_interactors(self):
        if self.vtkWidget:
            iren = self.vtkWidget.GetRenderWindow().GetInteractor()
            if iren:
                iren.Initialize()

    def reset_camera(self):
        if self.renderer:
            self.renderer.ResetCamera()
            self.render()

    def dispose(self):
        if self.scene_manager and hasattr(self.scene_manager, "events") and self.scene_manager.events:
            try:
                self.scene_manager.events.unsubscribe(
                    SceneEvents.SELECTION_CHANGED, self._on_selection_changed
                )
            except Exception:
                pass
        super().dispose()


if __name__ == "__main__":
    from application.scene.scene_manager import SceneManager
    from application.scene.scene_state import SceneState
    from application.scene.events.event_bus import EventBus
    from application.scene.registry.object_registry import ObjectRegistry
    from application.scene.registry.actor_registry import ActorRegistry
    from application.scene.selection.selection_manager import SelectionManager
    from application.scene.rendering.vtk_actor_factory import VTKActorFactory
    from application.scene.rendering.scene_bridge import SceneBridge
    from application.scene.io.importer import ObjectImporter
    import tempfile

    app = QtWidgets.QApplication(sys.argv)

    # Preparação das dependências
    event_bus = EventBus()
    state = SceneState()
    object_registry = ObjectRegistry()
    actor_registry = ActorRegistry()
    selection_manager = SelectionManager(state, event_bus)

    temp_patient_path = tempfile.mkdtemp()
    importer = ObjectImporter(patient_path=temp_patient_path)

    scene_manager = SceneManager(
        state=state,
        event_bus=event_bus,
        object_registry=object_registry,
        actor_registry=actor_registry,
        selection_manager=selection_manager,
        importer=importer,
        transform_manager=None,
    )


    class MockAppContext:
        def __init__(self, sm, em, tm):
            self.scene_manager = sm
            self.event_bus = em
            self.tool_manager = tm


    app_context = MockAppContext(scene_manager, event_bus, None)

    # Criação da janela utilizando a base herdada
    janela = Viewer3D_Widget_CentralArea(
        context=app_context, nome="Vista 3D", cor_borda="#00AAFF"
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