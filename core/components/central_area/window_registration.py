import sys
import logging
from typing import TYPE_CHECKING, Optional

from PySide6 import QtWidgets, QtCore, QtGui
import vtk

from core.shortcut.shortcuts import get_shortcuts_by_scope, match_shortcut
from core.components.menus.windows_registration_menu import WindowsRegistrationMenu
from core.components.central_area.windows_3d import Janela3DSurface

from core.scene.events.scene_events import SceneEvents, RegistrationEvents

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager


logger = logging.getLogger("OpenCMF.WindowRegistration")


class WindowRegistration(QtWidgets.QWidget):
    pontoAdicionado = QtCore.Signal(str, list)
    requisitarCarregamentoObjeto = QtCore.Signal(str, str)

    def __init__(self, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self._scene_manager = scene_manager
        self.shortcuts = get_shortcuts_by_scope("view3d")
        self.current_mode = "select"

        self.setup_ui()
        self._bind_scene_listeners()

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.top_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        for side in ["A", "B"]:
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)

            view = Janela3DSurface(f"Vista {side}", "#202020")
            combo = QtWidgets.QComboBox()

            layout.addWidget(view, stretch=1)
            layout.addWidget(combo)

            setattr(self, f"view_{side.lower()}", view)
            setattr(self, f"combo_{side.lower()}", combo)

            self.top_splitter.addWidget(container)

            combo.currentTextChanged.connect(
                lambda t, s=side: self._on_combo_changed(s, t)
            )

        self.view_c = Janela3DSurface("Visor Geral", "#202020")

        self.main_splitter.addWidget(self.top_splitter)
        self.main_splitter.addWidget(self.view_c)
        self.main_layout.addWidget(self.main_splitter)

    def _bind_scene_listeners(self) -> None:
        if not self._scene_manager:
            return

        bus = self._scene_manager.events
        bus.subscribe(SceneEvents.VISIBILITY_CHANGED, self._on_scene_bus_visibility)
        bus.subscribe(SceneEvents.OBJECT_UPDATED, self._on_scene_bus_object_updated)
        bus.subscribe(SceneEvents.OBJECT_REMOVED, self._on_scene_bus_object_removed)
        bus.subscribe(SceneEvents.INTERACTION_MODE_CHANGED, self.set_interaction_mode)

    def _on_combo_changed(self, vista_id: str, nome_objeto: str):
        if nome_objeto and self._scene_manager:
            self.requisitarCarregamentoObjeto.emit(vista_id, nome_objeto)

    def set_interaction_mode(self, mode: str, **kwargs):
        self.current_mode = mode
        cursor = QtCore.Qt.ArrowCursor if mode == "select" else QtCore.Qt.CrossCursor

        self.view_a.setCursor(cursor)
        self.view_b.setCursor(cursor)

        for view in [self.view_a, self.view_b]:
            view.set_interactor_style(mode)

    def _on_scene_bus_visibility(self, object_id: str, visible: bool, **_kwargs):
        for view in [self.view_a, self.view_b, self.view_c]:
            view.vtk_scene_renderer.set_visibility(object_id, visible)

    def _on_scene_bus_object_updated(self, object_id: str, **kwargs):
        prop = kwargs.get("property")
        val = kwargs.get("value")
        for view in [self.view_a, self.view_b, self.view_c]:
            view.vtk_scene_renderer.update_property(object_id, prop, val)

    def _on_scene_bus_object_removed(self, object_id: str, **_kwargs):
        for view in [self.view_a, self.view_b, self.view_c]:
            view.vtk_scene_renderer.remove_actor(object_id)
            view.render()

    def _get_active_view(self):
        for view in [self.view_a, self.view_b, self.view_c]:
            if view.hasFocus():
                return view
        return self.view_c

    def keyPressEvent(self, event):
        action = match_shortcut(event, self.shortcuts)
        if action:
            self.execute_action(action, self._get_active_view())
            event.accept()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    window.resize(1024, 768)

    registration_widget = WindowRegistration()
    window.setCentralWidget(registration_widget)

    window.show()
    sys.exit(app.exec())