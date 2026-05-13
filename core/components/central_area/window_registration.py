from PySide6 import QtWidgets, QtCore, QtGui
import vtk
import sys
import logging
from typing import TYPE_CHECKING, Optional

from core.components.central_area.windows_3d import Janela3DSurface
from core.scene.events.scene_events import (
    OBJECT_REMOVED,
    OBJECT_UPDATED,
    REGISTRATION_DELETE_LAST_MARKER,
    REGISTRATION_POINT_SIZE_CHANGED,
    REGISTRATION_RESET_LAYOUT,
    VISIBILITY_CHANGED,
    INTERACTION_MODE_CHANGED
)

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager

logger = logging.getLogger("OpenCMF.WindowRegistration")


class RegistrationDoubleClickFilter(QtCore.QObject):
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            return True
        return super().eventFilter(obj, event)


class WindowRegistration(QtWidgets.QWidget):
    pontoAdicionado = QtCore.Signal(str, list)
    requisitarCarregamentoObjeto = QtCore.Signal(str, str)

    def __init__(self, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self._scene_manager = scene_manager
        self.objetos_a = {}
        self.objetos_b = {}
        self.pontos_a = []
        self.pontos_b = []
        self.current_point_size = 1.5
        self.current_mode = "select"

        self.db_click_filter = RegistrationDoubleClickFilter(self)
        self.setMinimumSize(0, 0)
        self.setup_ui()
        self._bind_scene_listeners()

    def _bind_scene_listeners(self) -> None:
        if self._scene_manager is None:
            return
        bus = self._scene_manager.events
        bus.subscribe(VISIBILITY_CHANGED, self._on_scene_bus_visibility)
        bus.subscribe(OBJECT_UPDATED, self._on_scene_bus_object_updated)
        bus.subscribe(OBJECT_REMOVED, self._on_scene_bus_object_removed)
        bus.subscribe(REGISTRATION_DELETE_LAST_MARKER, self._on_scene_bus_delete_last_marker)
        bus.subscribe(REGISTRATION_RESET_LAYOUT, self._on_scene_bus_reset_layout)
        bus.subscribe(REGISTRATION_POINT_SIZE_CHANGED, self._on_scene_bus_point_size)
        bus.subscribe(INTERACTION_MODE_CHANGED, self.set_interaction_mode)

    def set_interaction_mode(self, mode: str, **kwargs):
        self.current_mode = mode
        cursor = QtCore.Qt.ArrowCursor if mode == "select" else QtCore.Qt.CrossCursor
        self.view_a.setCursor(cursor)
        self.view_b.setCursor(cursor)

        for view in [self.view_a, self.view_b]:
            interactor = view.vtkWidget.GetRenderWindow().GetInteractor()
            if mode == "select":
                style = vtk.vtkInteractorStyleTrackballCamera()
                interactor.SetInteractorStyle(style)
            else:
                style = vtk.vtkInteractorStyleUser()
                interactor.SetInteractorStyle(style)

    def _on_scene_bus_visibility(self, object_id: str, visible: bool, **_kwargs) -> None:
        self.set_objeto_visibilidade(object_id, visible)

    def _on_scene_bus_object_updated(self, object_id: str, **kwargs) -> None:
        prop = kwargs.get("property")
        value = kwargs.get("value")
        if prop == "opacity":
            self._apply_render_change("opacity", value, object_id)
        elif prop == "color":
            self._apply_render_change("color", value, object_id)

    def _on_scene_bus_object_removed(self, object_id: str, **_kwargs) -> None:
        if object_id in self.objetos_a:
            del self.objetos_a[object_id]
        if object_id in self.objetos_b:
            del self.objetos_b[object_id]
        for view in (self.view_a, self.view_b):
            view.vtk_scene_renderer.remove_actor(object_id)
            view.render()

    def _on_scene_bus_delete_last_marker(self, **_kwargs) -> None:
        self.remover_ultimo_marcador()

    def _on_scene_bus_reset_layout(self, **_kwargs) -> None:
        self.reset_layout_vistas()

    def _on_scene_bus_point_size(self, size=None, **_kwargs) -> None:
        if size is not None:
            self.set_ponto_raio(float(size))

    def remover_ultimo_marcador(self):
        for view, lista in [(self.view_a, self.pontos_a), (self.view_b, self.pontos_b)]:
            if not lista:
                continue
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            atores_na_cena = [actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
            for actor in reversed(atores_na_cena):
                if getattr(actor, "is_marker", False):
                    view.renderer.RemoveActor(actor)
                    lista.pop()
                    break
            view.render()

    def limpar_marcadores(self):
        for view, lista in [(self.view_a, self.pontos_a), (self.view_b, self.pontos_b)]:
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            atores_para_remover = []
            for _ in range(actors.GetNumberOfItems()):
                actor = actors.GetNextActor()
                if getattr(actor, "is_marker", False):
                    atores_para_remover.append(actor)
            for a in atores_para_remover:
                view.renderer.RemoveActor(a)
            lista.clear()
            view.render()

    def set_ponto_raio(self, novo_raio: float):
        self.current_point_size = novo_raio
        for view in [self.view_a, self.view_b]:
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            for _ in range(actors.GetNumberOfItems()):
                actor = actors.GetNextActor()
                if getattr(actor, "is_marker", False):
                    source = actor.GetMapper().GetInputAlgorithm()
                    if isinstance(source, vtk.vtkSphereSource):
                        source.SetRadius(novo_raio)
                    view.render()

    def set_objeto_visibilidade(self, identifier: str, visivel: bool):
        for view in [self.view_a, self.view_b]:
            actor = self._find_actor_by_id(view, identifier)
            if actor:
                actor.SetVisibility(visivel)
                view.render()

    def connect_properties_panel(self, properties_panel) -> None:
        if not properties_panel:
            return
        properties_panel.positionChanged.connect(lambda pos: self._apply_transform_change("position", pos))
        properties_panel.rotationChanged.connect(lambda rot: self._apply_transform_change("rotation", rot))
        properties_panel.scaleChanged.connect(lambda scl: self._apply_transform_change("scale", scl))

        if self._scene_manager is not None:
            properties_panel.colorChanged.connect(self._properties_color_via_scene)
            properties_panel.opacityChanged.connect(self._properties_opacity_via_scene)
        else:
            properties_panel.colorChanged.connect(
                lambda id_obj, col: self._apply_render_change("color", col, id_obj)
            )
            properties_panel.opacityChanged.connect(
                lambda id_obj, op: self._apply_render_change("opacity", op, id_obj)
            )

    def _properties_color_via_scene(self, id_obj: str, col: QtGui.QColor) -> None:
        self._scene_manager.update_color(
            id_obj, (col.redF(), col.greenF(), col.blueF())
        )

    def _properties_opacity_via_scene(self, id_obj: str, op: float) -> None:
        self._scene_manager.update_opacity(id_obj, op)

    def _find_actor_by_id(self, view, identifier):
        actors = view.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if getattr(actor, "id", None) == identifier or getattr(actor, "name", None) == identifier:
                return actor
        return None

    def adicionar_malha_vista_a(self, nome, polydata, obj_id=None):
        self._limpar_atores_da_vista(self.view_a)
        identifier = obj_id or nome
        self.objetos_a = {identifier: polydata}
        self.view_a.adicionar_objeto(identifier, polydata, cor=(0.7, 0.7, 0.9), nome_amigavel=nome)
        self.view_a.render()

    def adicionar_malha_vista_b(self, nome, polydata, obj_id=None):
        self._limpar_atores_da_vista(self.view_b)
        identifier = obj_id or nome
        self.objetos_b = {identifier: polydata}
        self.view_b.adicionar_objeto(identifier, polydata, cor=(0.9, 0.9, 0.7), nome_amigavel=nome)
        self.view_b.render()

    def _apply_render_change(self, render_type, value, identifier=None):
        for view in [self.view_a, self.view_b]:
            if identifier:
                target = self._find_actor_by_id(view, identifier)
                actors = [target] if target else []
            else:
                actors = []
                it = view.renderer.GetActors()
                it.InitTraversal()
                for _ in range(it.GetNumberOfItems()):
                    a = it.GetNextActor()
                    if not getattr(a, "is_marker", False):
                        actors.append(a)
            for actor in actors:
                if not actor: continue
                prop = actor.GetProperty()
                if render_type == "color":
                    if isinstance(value, QtGui.QColor):
                        prop.SetColor(value.redF(), value.greenF(), value.blueF())
                    else:
                        prop.SetColor(value)
                elif render_type == "opacity":
                    prop.SetOpacity(value)
                view.render()

    def _apply_transform_change(self, transform_type, values):
        for view in [self.view_a, self.view_b]:
            it = view.renderer.GetActors()
            it.InitTraversal()
            for _ in range(it.GetNumberOfItems()):
                actor = it.GetNextActor()
                if not getattr(actor, "is_marker", False):
                    if transform_type == "position":
                        actor.SetPosition(values)
                    elif transform_type == "rotation":
                        actor.SetOrientation(values)
                    elif transform_type == "scale":
                        actor.SetScale(values)
            view.render()

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        for side in ["A", "B"]:
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(4, 4, 4, 4)
            view = Janela3DSurface(f"Vista {side}", "#202020")
            view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            controls_layout = QtWidgets.QHBoxLayout()
            combo_mesh = QtWidgets.QComboBox()
            combo_mesh.setPlaceholderText("Selecionar objeto...")
            combo_view = QtWidgets.QComboBox()
            combo_view.addItems(["Frontal", "Posterior", "Direita", "Esquerda", "Superior", "Inferior"])
            combo_view.setFixedWidth(110)
            controls_layout.addWidget(combo_mesh, stretch=1)
            controls_layout.addWidget(combo_view)
            layout.addWidget(view, stretch=1)
            layout.addWidget(QtWidgets.QLabel("Referência (Fixo):" if side == "A" else "Móvel (Alinhamento):"))
            layout.addLayout(controls_layout)
            setattr(self, f"view_{side.lower()}", view)
            setattr(self, f"combo_{side.lower()}", combo_mesh)
            self.splitter.addWidget(container)
            combo_view.currentTextChanged.connect(lambda t, s=side: self._on_view_presets_changed(s, t))
        self.main_layout.addWidget(self.splitter)
        self.combo_a.currentTextChanged.connect(lambda t: self._on_combo_changed("A", t))
        self.combo_b.currentTextChanged.connect(lambda t: self._on_combo_changed("B", t))
        QtCore.QTimer.singleShot(100, self._finalize_setup)

    def _on_view_presets_changed(self, side, view_name):
        view = self.view_a if side == "A" else self.view_b
        camera = view.renderer.GetActiveCamera()
        presets = {
            "Frontal": ([0, 0, 0], [0, 0, 1], [0, 1, 0]),
            "Posterior": ([0, 0, 0], [0, 0, -1], [0, 1, 0]),
            "Direita": ([0, 0, 0], [1, 0, 0], [0, 1, 0]),
            "Esquerda": ([0, 0, 0], [-1, 0, 0], [0, 1, 0]),
            "Superior": ([0, 0, 0], [0, 1, 0], [0, 0, -1]),
            "Inferior": ([0, 0, 0], [0, -1, 0], [0, 0, 1]),
        }
        if view_name in presets:
            f, p, u = presets[view_name]
            camera.SetFocalPoint(*f)
            camera.SetPosition(*p)
            camera.SetViewUp(*u)
            view.renderer.ResetCamera()
            view.render()

    def _limpar_atores_da_vista(self, view):
        renderer = view.renderer
        actors = renderer.GetActors()
        actors.InitTraversal()
        to_remove = []
        for _ in range(actors.GetNumberOfItems()):
            a = actors.GetNextActor()
            if not getattr(a, "is_marker", False):
                to_remove.append(a)
        for a in to_remove:
            renderer.RemoveActor(a)
        view.vtk_scene_renderer.reset_tracked_actors()

    def atualizar_lista_objetos(self, nomes_objetos: list):
        for combo in [self.combo_a, self.combo_b]:
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("")
            combo.addItems(nomes_objetos)
            combo.blockSignals(False)

    def _on_combo_changed(self, vista_id, nome_objeto):
        if nome_objeto:
            self.requisitarCarregamentoObjeto.emit(vista_id, nome_objeto)

    def _finalize_setup(self):
        self.view_a.setup_interactors()
        self.view_b.setup_interactors()
        self.view_a.vtkWidget.GetRenderWindow().GetInteractor().AddObserver("LeftButtonPressEvent", self._on_click_a)
        self.view_b.vtkWidget.GetRenderWindow().GetInteractor().AddObserver("LeftButtonPressEvent", self._on_click_b)
        self.reset_layout_vistas()

    def reset_layout_vistas(self):
        w = self.splitter.width()
        if w > 0:
            self.splitter.setSizes([w // 2, w // 2])
        self.view_a.render()
        self.view_b.render()

    def _on_click_a(self, obj, event):
        if self.current_mode == "select": return
        self._pick_point(self.view_a, "A", self.pontos_a, (1, 0, 0))

    def _on_click_b(self, obj, event):
        if self.current_mode == "select": return
        self._pick_point(self.view_b, "B", self.pontos_b, (0, 1, 0))

    def _pick_point(self, view, side_label, points_list, color):
        interactor = view.vtkWidget.GetRenderWindow().GetInteractor()
        x, y = interactor.GetEventPosition()
        picker = vtk.vtkPointPicker()
        picker.Pick(x, y, 0, view.renderer)
        pos = picker.GetPickPosition()
        if any(pos):
            points_list.append(pos)
            self._desenhar_ponto(view, pos, color)
            self.pontoAdicionado.emit(side_label, list(pos))

    def _desenhar_ponto(self, view, pos, cor):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(pos)
        sphere.SetRadius(self.current_point_size)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(cor)
        actor.is_marker = True
        view.renderer.AddActor(actor)
        view.render()

    def get_points_a(self): return self.pontos_a
    def get_points_b(self): return self.pontos_b


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.resize(1024, 768)
    registration_widget = WindowRegistration()
    window.setCentralWidget(registration_widget)
    window.show()
    sys.exit(app.exec())