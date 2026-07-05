import sys
import logging
from typing import TYPE_CHECKING, Optional
from PySide6 import QtWidgets, QtCore, QtGui
import vtk

from core.shortcut.shortcuts import get_shortcuts_by_scope, match_shortcut
from core.components.menus.windows_registration_menu import WindowsRegistrationMenu
from core.components.central_area.windows_3d import Janela3DSurface
from core.scene.events.scene_events import (
    OBJECT_REMOVED, OBJECT_UPDATED, REGISTRATION_DELETE_LAST_MARKER,
    REGISTRATION_POINT_SIZE_CHANGED, REGISTRATION_RESET_LAYOUT,
    VISIBILITY_CHANGED, INTERACTION_MODE_CHANGED
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
        self.objetos_a, self.objetos_b = {}, {}
        self.pontos_a, self.pontos_b = [], {}
        self.current_point_size = 1.5
        self.current_mode = "select"

        self.setup_ui()
        self._bind_scene_listeners()
        self.shortcuts = get_shortcuts_by_scope("view3d")

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.top_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        for side in ["A", "B"]:
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            view = Janela3DSurface(f"Vista {side}", "#202020")
            layout.addWidget(view, stretch=1)

            combo = QtWidgets.QComboBox()
            combo.setPlaceholderText("Referência" if side == "A" else "Móvel")
            layout.addWidget(combo)

            setattr(self, f"view_{side.lower()}", view)
            setattr(self, f"combo_{side.lower()}", combo)
            self.top_splitter.addWidget(container)
            combo.currentTextChanged.connect(lambda t, s=side: self._on_combo_changed(s, t))

        self.main_splitter.addWidget(self.top_splitter)
        self.view_c = Janela3DSurface("Visor Geral", "#202020")
        self.view_c.header.hide()
        self.main_splitter.addWidget(self.view_c)
        self.main_layout.addWidget(self.main_splitter)

    def showEvent(self, event):
        super().showEvent(event)
        self._init_vtk_resources()

    def _init_vtk_resources(self):

        for v in [self.view_a, self.view_b, self.view_c]:
            v.setup_interactors()
            v.setFocusPolicy(QtCore.Qt.StrongFocus)
            v.installEventFilter(self)

        self.view_a.vtkWidget.GetRenderWindow().GetInteractor().AddObserver("LeftButtonPressEvent", self._on_click_a)
        self.view_b.vtkWidget.GetRenderWindow().GetInteractor().AddObserver("LeftButtonPressEvent", self._on_click_b)

        self._connect_context_menus()
        self._setup_keyboard_focus()
        self.reset_layout_vistas()
        self.view_c.setFocus()


    def reset_layout_vistas(self):
        w = self.top_splitter.width()
        h = self.main_splitter.height()
        if w > 0: self.top_splitter.setSizes([w // 2, w // 2])
        if h > 0: self.main_splitter.setSizes([h // 2, h // 2])

        self.view_a.render()
        self.view_b.render()
        self.view_c.render()

    def _connect_context_menus(self):
        for side, view in [("A", self.view_a), ("B", self.view_b)]:
            view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            view.customContextMenuRequested.connect(lambda pos, s=side: self._open_context_menu(s, pos))

    def _open_context_menu(self, side: str, position: QtCore.QPoint):
        view = self.view_a if side == "A" else self.view_b
        menu = WindowsRegistrationMenu(self, view, side)
        menu.exec(view.mapToGlobal(position))

 
    def atualizar_lista_objetos(self, nomes_objetos: list):
        if not nomes_objetos:
            return

        for combo in [self.combo_a, self.combo_b]:
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("")
            combo.addItems(nomes_objetos)
            combo.blockSignals(False)

        if nomes_objetos:
            self.combo_a.setCurrentText(nomes_objetos[0])

        if len(nomes_objetos) > 1:
            self.combo_b.setCurrentText(nomes_objetos[1])
        elif nomes_objetos:
            self.combo_b.setCurrentText(nomes_objetos[0])

    def _verificar_e_atualizar_vistas(self):
        objeto_a_carregado = len(self.objetos_a) > 0
        objeto_b_carregado = len(self.objetos_b) > 0

        logger.debug(f"Objeto A carregado: {objeto_a_carregado}, Objeto B carregado: {objeto_b_carregado}")

        if objeto_a_carregado and objeto_b_carregado:
            logger.debug("Ambos objetos carregados, atualizando vistas para frontal")
            self._atualizar_vistas_para_frontal()
        else:
            QtCore.QTimer.singleShot(100, self._verificar_e_atualizar_vistas)

    def _atualizar_vistas_para_frontal(self):
        for view_name, view in [("A", self.view_a), ("B", self.view_b), ("C", self.view_c)]:
            if not view.renderer:
                logger.warning(f"View {view_name}: renderer não encontrado")
                continue

            camera = view.renderer.GetActiveCamera()
            camera.SetPosition(0, -100, 0)
            camera.SetViewUp(0, 0, 1)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetParallelProjection(False)

            view.renderer.ResetCamera()
            view.render()
            view.render()

            logger.debug(f"View {view_name} atualizada para orientação frontal")

        self.reset_layout_vistas()

    def _on_combo_changed(self, vista_id, nome_objeto):
        if nome_objeto:
            self.requisitarCarregamentoObjeto.emit(vista_id, nome_objeto)
            QtCore.QTimer.singleShot(100, self._verificar_e_atualizar_vistas)

    def adicionar_malha_vista_a(self, nome, polydata, obj_id=None):
        self._limpar_atores_da_vista(self.view_a)
        for prev_id in list(self.objetos_a.keys()):
            self.view_c.del_object(prev_id)

        identifier = obj_id or nome
        self.objetos_a = {identifier: polydata}

        self.view_a.add_object(identifier, polydata, cor=(0.7, 0.7, 0.9), nome_amigavel=nome)
        self.view_c.add_object(identifier, polydata, cor=(0.7, 0.7, 0.9), nome_amigavel=nome)
        self.view_a.render()
        self.view_c.render()

        QtCore.QTimer.singleShot(50, self._verificar_e_atualizar_vistas)

    def adicionar_malha_vista_b(self, nome, polydata, obj_id=None):
        self._limpar_atores_da_vista(self.view_b)
        for prev_id in list(self.objetos_b.keys()):
            self.view_c.del_object(prev_id)

        identifier = obj_id or nome
        self.objetos_b = {identifier: polydata}

        self.view_b.add_object(identifier, polydata, cor=(0.9, 0.9, 0.7), nome_amigavel=nome)
        self.view_c.add_object(identifier, polydata, cor=(0.9, 0.9, 0.7), nome_amigavel=nome)
        self.view_b.render()
        self.view_c.render()

        QtCore.QTimer.singleShot(50, self._verificar_e_atualizar_vistas)

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
        self.objetos_a.pop(object_id, None)
        self.objetos_b.pop(object_id, None)
        for view in (self.view_a, self.view_b, self.view_c):
            view.vtk_scene_renderer.remove_actor(object_id)
            view.render()

    def _on_scene_bus_delete_last_marker(self, **_kwargs) -> None:
        self.remover_ultimo_marcador()

    def _on_scene_bus_reset_layout(self, **_kwargs) -> None:
        self.reset_layout_vistas()

    def _on_scene_bus_point_size(self, size=None, **_kwargs) -> None:
        if size is not None:
            self.set_ponto_raio(float(size))

    def set_objeto_visibilidade(self, identifier: str, visivel: bool):
        for view in [self.view_a, self.view_b, self.view_c]:
            actor = self._find_actor_by_id(view, identifier)
            if actor:
                actor.SetVisibility(visivel)
                view.render()

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

    def _find_actor_by_id(self, view, identifier):
        actors = view.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if (getattr(actor, "id", None) == identifier or
                    getattr(actor, "name", None) == identifier):
                return actor
        return None

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

    def _apply_render_change(self, render_type, value, identifier=None):
        for view in [self.view_a, self.view_b, self.view_c]:
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
                if not actor:
                    continue
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
        for view in [self.view_a, self.view_b, self.view_c]:
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

    def connect_properties_panel(self, properties_panel) -> None:
        if not properties_panel:
            return
        pass

    def _properties_color_via_scene(self, id_obj: str, col: QtGui.QColor) -> None:
        if self._scene_manager:
            self._scene_manager.update_color(id_obj, (col.redF(), col.greenF(), col.blueF()))

    def _properties_opacity_via_scene(self, id_obj: str, op: float) -> None:
        if self._scene_manager:
            self._scene_manager.update_opacity(id_obj, op)

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

    def _on_click_a(self, obj, event):
        if self.current_mode == "select":
            return
        self._pick_point(self.view_a, "A", self.pontos_a, (1, 0, 0))

    def _on_click_b(self, obj, event):
        if self.current_mode == "select":
            return
        self._pick_point(self.view_b, "B", self.pontos_b, (0, 1, 0))

    def get_points_a(self):
        return self.pontos_a

    def get_points_b(self):
        return self.pontos_b

    def keyPressEvent(self, event):
        action = match_shortcut(event, self.shortcuts)

        if action:
            active_view = self._get_active_view()
            if active_view:
                self.execute_action(action, active_view)
                event.accept()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def _get_active_view(self):
        if self.view_a.hasFocus():
            return self.view_a
        elif self.view_b.hasFocus():
            return self.view_b
        elif self.view_c.hasFocus():
            return self.view_c
        return self.view_c

    def execute_action(self, action_id: str, view):
        view_maps = {
            "view3d.frontal": {
                "position": (0, -100, 0),
                "view_up": (0, 0, 1),
                "focal": (0, 0, 0)
            },
            "view3d.right": {
                "position": (100, 0, 0),
                "view_up": (0, 0, 1),
                "focal": (0, 0, 0)
            },
            "view3d.left": {
                "position": (-100, 0, 0),
                "view_up": (0, 0, 1),
                "focal": (0, 0, 0)
            },
            "view3d.superior": {
                "position": (0, 0, 100),
                "view_up": (0, 1, 0),
                "focal": (0, 0, 0)
            },
            "view3d.inferior": {
                "position": (0, 0, -100),
                "view_up": (0, -1, 0),
                "focal": (0, 0, 0)
            },
        }

        if action_id in view_maps:
            cam = view.renderer.GetActiveCamera()
            config = view_maps[action_id]

            cam.SetPosition(config["position"])
            cam.SetViewUp(config["view_up"])
            cam.SetFocalPoint(config["focal"])

            view.renderer.ResetCamera()
            view.render()
            logger.debug(f"View alterada para: {action_id}")
            return

        elif action_id == "view3d.orthogonal":
            cam = view.renderer.GetActiveCamera()
            current = cam.GetParallelProjection()
            cam.SetParallelProjection(not current)
            view.render()
            logger.debug(f"Projeção alterada: {'Ortogonal' if not current else 'Perspectiva'}")
            return

        elif action_id == "view3d.delete_object":
            if self._scene_manager and hasattr(self._scene_manager, 'selection'):
                selected_ids = list(self._scene_manager.selection.selected_ids)
                if selected_ids:
                    self._scene_manager.selection.clear()
                    for obj_id in selected_ids:
                        self._scene_manager.remove_object(obj_id)
                    for v in [self.view_a, self.view_b, self.view_c]:
                        v.render()
                    logger.debug(f"Objetos deletados: {selected_ids}")
            return

        elif action_id in ["view3d.mandible", "view3d.maxilla", "view3d.skull", "view3d.chin"]:
            anatomy_keywords = {
                "view3d.mandible": ["mandibula", "mandible"],
                "view3d.maxilla": ["maxila", "maxilla"],
                "view3d.skull": ["cranio", "skull"],
                "view3d.chin": ["mento", "queixo", "chin"],
            }

            keywords = anatomy_keywords[action_id]
            target_actor = None
            target_id = None

            for v in [self.view_a, self.view_b, self.view_c]:
                if hasattr(v, 'vtk_scene_renderer'):
                    actors = v.vtk_scene_renderer.get_actors()
                    for obj_id, actor in actors.items():
                        actor_name = getattr(actor, "name", "") or ""
                        if any(kw in obj_id.lower() or kw in actor_name.lower() for kw in keywords):
                            target_actor = actor
                            target_id = obj_id
                            break
                if target_actor:
                    break

            if target_id and self._scene_manager:
                self._scene_manager.selection.select(target_id, exclusive=True)

            if target_actor:
                bounds = target_actor.GetBounds()
                if bounds and all(b is not None for b in bounds):
                    view.renderer.ResetCamera(bounds)
                    view.render()
                    logger.debug(f"Focado em: {action_id} (ID: {target_id})")
            return

    def _setup_keyboard_focus(self):
        for view in [self.view_a, self.view_b, self.view_c]:
            view.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            view.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)
            view.installEventFilter(self)
            vtk_widget = view.vtkWidget
            vtk_widget.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            vtk_widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            for v in [self.view_a, self.view_b, self.view_c]:
                if obj in [v, v.vtkWidget]: v.setFocus()
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.resize(1024, 768)
    registration_widget = WindowRegistration()
    window.setCentralWidget(registration_widget)
    window.show()
    sys.exit(app.exec())