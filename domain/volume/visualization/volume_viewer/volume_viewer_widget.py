import sys
from pathlib import Path
from typing import Optional, Any

from PySide6 import QtWidgets, QtCore
import vtk

# Scene
from application.scene.scene_object import SceneObject
from application.scene.events.scene_events import SceneEvents

# Settings
raiz_projeto = Path(__file__).resolve().parent.parent.parent.parent
if str(raiz_projeto) not in sys.path:
    sys.path.insert(0, str(raiz_projeto))

from core.settings.paths.list_paths import PRESETS_DIR

# Modular structure imports
from domain.volume.visualization.volume_viewer.constants import VolumeViewerConstants
from domain.volume.visualization.volume_viewer.volume_viewer_factory import VolumeViewerFactory
from domain.volume.visualization.volume_viewer.viewer_controller import VolumeViewerController


class VolumeViewerWidget(QtWidgets.QWidget):
    sliceChanged = QtCore.Signal(str, int)
    windowLevelChanged = QtCore.Signal(float, float)

    def __init__(self, event_bus: Any, object_registry: Any, context: Optional[Any] = None, parent=None):
        super().__init__(parent)

        if event_bus is None:
            raise ValueError("VolumeViewerWidget: event_bus cannot be None")
        if object_registry is None:
            raise ValueError("VolumeViewerWidget: object_registry cannot be None")

        self.events = event_bus
        self.registry = object_registry
        self.context = context

        self._init_paths()

        # Visual instances dictionaries
        self.vistas = {}

        # Viewer creation via Factory
        callbacks = {
            'self_ref': self,
            'on_slice_changed': self._on_slice_changed_proxy,
            'on_maximize': self._handle_maximize,
            'on_lut_changed': self.apply_global_lut,
            'on_threshold_changed': self._on_threshold_changed_proxy,
            'on_3d_view_changed': self._on_3d_view_changed_proxy,
            'on_preset_changed': self._on_preset_changed_proxy
        }

        self.vistas = VolumeViewerFactory.create_viewers(
            context=self.context,
            event_bus=self.events,
            registry=self.registry,
            callbacks=callbacks
        )

        # VTK Logic Controller
        self.controller = VolumeViewerController(self.vistas, self.path_presets)

        # EventBus Subscriptions
        self.events.subscribe(SceneEvents.OBJECT_ADDED, self._on_object_added)
        self.events.subscribe(SceneEvents.OBJECT_REMOVED, self._on_object_removed)
        self.events.subscribe("LAYOUT_CHANGED", self._on_layout_event_received)

        self._setup_ui()

    def _init_paths(self):
        self.path_presets = str(PRESETS_DIR)

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(2)

        layout.addWidget(self.grid_container)

        self.configure_layout("4 Quadrants")

    def _on_layout_event_received(self, layout: str):
        """Ouve o evento global de layout e atualiza a interface automaticamente."""
        self.configure_layout(layout)

    def _on_object_added(self, object_id: str, obj: SceneObject):
        if obj.type == "volume":
            self.controller.volume_object = obj
            volume_data = obj.metadata.get("volume_data")
            if volume_data:
                self.set_volume(volume_data)

    def set_volume(self, volume: vtk.vtkImageData):
        """Public method to directly inject the volume."""
        if volume:
            self.controller.render_volume(volume)
            viewer_3d = self.vistas.get("3D")
            if viewer_3d and hasattr(viewer_3d, 'combo_presets'):
                preset = viewer_3d.combo_presets.currentText()
                if preset:
                    QtCore.QTimer.singleShot(50, lambda: self.controller.update_preset(preset))

    def apply_global_lut(self, lut_name: str):
        self.controller.apply_global_lut(lut_name, None)

    def _on_slice_changed_proxy(self, plano: str, index: int):
        self.controller.update_slice(plano, index)
        self.sliceChanged.emit(plano, index)

    def _on_threshold_changed_proxy(self, value: int):
        self.controller.update_threshold(value)

    def _on_3d_view_changed_proxy(self, vista: str):
        self.controller.update_3d_view(vista)

    def _on_preset_changed_proxy(self, nome: str):
        self.controller.update_preset(nome)

    def configure_layout(self, mode: str):
        for i in reversed(range(self.grid_layout.count())):
            if w := self.grid_layout.itemAt(i).widget():
                w.setParent(None)

        for n, obj in self.vistas.items():
            obj.hide()
            if hasattr(obj, 'is_maximized'):
                obj.is_maximized = (mode == n or (mode == "3D Only" and n == "3D"))
                obj._update_maximize_icon()

        mapping = {
            "4 Quadrants": [("Axial", 0, 0), ("Sagittal", 0, 1), ("Coronal", 1, 0), ("3D", 1, 1)],
            "Highlighted 3D": [("Axial", 0, 0), ("Sagittal", 0, 1), ("Coronal", 0, 2), ("3D", 1, 0, 1, 3)],
            "3D Only": [("3D", 0, 0)], "Axial": [("Axial", 0, 0)],
            "Sagittal": [("Sagittal", 0, 0)], "Coronal": [("Coronal", 0, 0)]
        }
        for item in mapping.get(mode, []):
            self.grid_layout.addWidget(self.vistas[item[0]], *item[1:])
            self.vistas[item[0]].show()

    def _handle_maximize(self, name: str, is_max: bool):
        mode = (name if name != "3D" else "3D Only") if is_max else "4 Quadrants"
        self.configure_layout(mode)

    def refresh_display(self):
        for p in self.vistas.values():
            if p.isVisible():
                p.vtkWidget.GetRenderWindow().Render()

    def _on_object_removed(self, object_id: str):
        if self.controller.volume_object and self.controller.volume_object.id == object_id:
            self.controller.clear_scene()


if __name__ == "__main__":
    class DummyManager:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None


    class DummyBus:
        def subscribe(self, event, callback): pass
        def emit(self, event, *args, **kwargs): pass


    class MockContext:
        def __init__(self):
            self.event_bus = DummyBus()
            self.scene_manager = DummyManager()
            self.tool_manager = DummyManager()


    class DummyRegistry:
        pass


    app = QtWidgets.QApplication(sys.argv)

    event_bus = DummyBus()
    registry = DummyRegistry()
    mock_context = MockContext()

    viewer = VolumeViewerWidget(
        event_bus=event_bus,
        object_registry=registry,
        context=mock_context
    )
    viewer.resize(1024, 768)
    viewer.setWindowTitle("Test - Volume Viewer")
    viewer.show()

    sys.exit(app.exec())