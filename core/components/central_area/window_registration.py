from PySide6 import QtWidgets, QtCore, QtGui
import vtk
import sys
import logging
from core.components.central_area.windows_3d import Janela3DSurface

logger = logging.getLogger("OpenCMF.WindowRegistration")


class RegistrationDoubleClickFilter(QtCore.QObject):
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            return True
        return super().eventFilter(obj, event)


class WindowRegistration(QtWidgets.QWidget):
    pontoAdicionado = QtCore.Signal(str, list)
    requisitarCarregamentoObjeto = QtCore.Signal(str, str)

    def __init__(self):
        super().__init__()
        self.objetos_a = {}
        self.objetos_b = {}
        self.pontos_a = []
        self.pontos_b = []
        self.current_point_size = 1.5
        self.db_click_filter = RegistrationDoubleClickFilter(self)
        self.setMinimumSize(0, 0)
        self.setup_ui()

    def connect_properties_panel(self, properties_panel) -> None:
        if properties_panel:
            properties_panel.positionChanged.connect(lambda pos: self._apply_transform_change("position", pos))
            properties_panel.rotationChanged.connect(lambda rot: self._apply_transform_change("rotation", rot))
            properties_panel.scaleChanged.connect(lambda scl: self._apply_transform_change("scale", scl))
            properties_panel.colorChanged.connect(lambda col: self._apply_render_change("color", col))
            properties_panel.opacityChanged.connect(lambda op: self._apply_render_change("opacity", op))
            properties_panel.representationChanged.connect(lambda rep: self._apply_render_change("representation", rep))
            properties_panel.ambientChanged.connect(lambda amb: self._apply_render_change("ambient", amb))
            properties_panel.diffuseChanged.connect(lambda dif: self._apply_render_change("diffuse", dif))
            properties_panel.specularChanged.connect(lambda spec: self._apply_render_change("specular", spec))
            properties_panel.specularPowerChanged.connect(lambda pwr: self._apply_render_change("specular_power", pwr))
            properties_panel.edgeVisibilityChanged.connect(
                lambda vis: self._apply_render_change("edge_visibility", vis))

    def _apply_transform_change(self, transform_type: str, values: list) -> None:
        for view_name, objetos in [("A", self.objetos_a), ("B", self.objetos_b)]:
            for identifier in objetos.keys():
                self._apply_transform_to_object(view_name, identifier, transform_type, values)

    def _apply_render_change(self, render_type: str, value) -> None:
        for view_name, objetos in [("A", self.objetos_a), ("B", self.objetos_b)]:
            for identifier in objetos.keys():
                self._apply_render_to_object(view_name, identifier, render_type, value)

    def set_objeto_visibilidade(self, identifier: str, visivel: bool):
        for view in [self.view_a, self.view_b]:
            actor = self._find_actor_by_id(view, identifier)
            if actor:
                actor.SetVisibility(visivel)
            view.render()

    def set_objeto_opacidade(self, identifier: str, valor: float):
        for view in [self.view_a, self.view_b]:
            actor = self._find_actor_by_id(view, identifier)
            if actor:
                actor.GetProperty().SetOpacity(valor)
            view.render()

    def set_objeto_cor(self, identifier: str, cor_rgb):
        for view in [self.view_a, self.view_b]:
            actor = self._find_actor_by_id(view, identifier)
            if actor:
                actor.GetProperty().SetColor(cor_rgb)
            view.render()

    def _find_actor_by_id(self, view, identifier):
        actors = view.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            # Verifica ID (UUID) ou Nome para compatibilidade
            actor_id = getattr(actor, "id", None)
            actor_name = getattr(actor, "name", None)
            if identifier in [actor_id, actor_name]:
                return actor
        return None

    def _apply_transform_to_object(self, view_name: str, identifier: str, transform_type: str, values: list) -> None:
        view = self.view_a if view_name == "A" else self.view_b
        actor = self._find_actor_by_id(view, identifier)
        if actor:
            if transform_type == "position":
                actor.SetPosition(values)
            elif transform_type == "rotation":
                actor.SetOrientation(values)
            elif transform_type == "scale":
                actor.SetScale(values)
        view.render()

    def _apply_render_to_object(self, view_name: str, identifier: str, render_type: str, value) -> None:
        view = self.view_a if view_name == "A" else self.view_b
        actor = self._find_actor_by_id(view, identifier)
        if actor:
            prop = actor.GetProperty()
            if render_type == "color":
                if isinstance(value, QtGui.QColor):
                    prop.SetColor(value.redF(), value.greenF(), value.blueF())
                else:
                    prop.SetColor(value)
            elif render_type == "opacity":
                prop.SetOpacity(value)
            elif render_type == "representation":
                v = value.lower() if isinstance(value, str) else ""
                if v == "surface":
                    prop.SetRepresentationToSurface()
                elif v == "wireframe":
                    prop.SetRepresentationToWireframe()
                elif v == "points":
                    prop.SetRepresentationToPoints()
            elif render_type == "ambient":
                prop.SetAmbient(value)
            elif render_type == "diffuse":
                prop.SetDiffuse(value)
            elif render_type == "specular":
                prop.SetSpecular(value)
            elif render_type == "specular_power":
                prop.SetSpecularPower(value)
            elif render_type == "edge_visibility":
                prop.SetEdgeVisibility(value)
        view.render()

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        for side in ["A", "B"]:
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(4, 4, 4, 4)

            view = Janela3DSurface(f"Vista {side}", "#00AAFF" if side == "A" else "#555555")
            view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

            combo = QtWidgets.QComboBox()
            combo.setPlaceholderText(f"Selecionar objeto Vista {side}...")

            layout.addWidget(view, stretch=1)
            layout.addWidget(QtWidgets.QLabel("Objeto de Referência:" if side == "A" else "Objeto Móvel:"))
            layout.addWidget(combo)

            setattr(self, f"view_{side.lower()}", view)
            setattr(self, f"combo_{side.lower()}", combo)
            self.splitter.addWidget(container)

        self.main_layout.addWidget(self.splitter)
        self.combo_a.currentTextChanged.connect(lambda t: self._on_combo_changed("A", t))
        self.combo_b.currentTextChanged.connect(lambda t: self._on_combo_changed("B", t))
        QtCore.QTimer.singleShot(100, self._finalize_setup)

    def _finalize_setup(self):
        self.setup_interactors()
        self.reset_layout_vistas()

    def setup_interactors(self):
        self.view_a.setup_interactors()
        self.view_b.setup_interactors()
        for view, p_attr, handler in [(self.view_a, 'picker_a', self._on_click_a),
                                      (self.view_b, 'picker_b', self._on_click_b)]:
            interactor = view.vtkWidget.GetRenderWindow().GetInteractor()
            picker = vtk.vtkPointPicker()
            setattr(self, p_attr, picker)
            interactor.SetPicker(picker)
            interactor.AddObserver("LeftButtonPressEvent", handler)

    def reset_layout_vistas(self):
        w = self.splitter.width()
        if w > 0: self.splitter.setSizes([w // 2, w // 2])
        self.view_a.reset_camera()
        self.view_b.reset_camera()
        self.view_a.render()
        self.view_b.render()

    def atualizar_lista_objetos(self, nomes_objetos: list):
        for combo in [self.combo_a, self.combo_b]:
            current = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("")
            combo.addItems(nomes_objetos)
            if current in nomes_objetos: combo.setCurrentText(current)
            combo.blockSignals(False)

    def _on_combo_changed(self, vista_id, nome_objeto):
        if nome_objeto: self.requisitarCarregamentoObjeto.emit(vista_id, nome_objeto)

    def adicionar_malha_vista_a(self, nome, polydata, obj_id=None):
        self._limpar_atores_da_vista(self.view_a)
        identifier = obj_id or nome
        self.objetos_a = {identifier: polydata}
        self.view_a.adicionar_objeto(nome, polydata, cor=(0.7, 0.7, 0.9))
        actor = self._find_actor_by_id(self.view_a, nome)
        if actor: actor.id = identifier
        self.view_a.render()

    def adicionar_malha_vista_b(self, nome, polydata, obj_id=None):
        self._limpar_atores_da_vista(self.view_b)
        identifier = obj_id or nome
        self.objetos_b = {identifier: polydata}
        self.view_b.adicionar_objeto(nome, polydata, cor=(0.9, 0.9, 0.7))
        actor = self._find_actor_by_id(self.view_b, nome)
        if actor: actor.id = identifier
        self.view_b.render()

    def remover_objeto(self, identifier):
        self.view_a.remover_objeto(identifier)
        self.view_b.remover_objeto(identifier)
        self.objetos_a.pop(identifier, None)
        self.objetos_b.pop(identifier, None)
        self.view_a.render()
        self.view_b.render()

    def limpar_vistas_total(self):
        self._limpar_atores_da_vista(self.view_a)
        self._limpar_atores_da_vista(self.view_b)
        self.objetos_a.clear()
        self.objetos_b.clear()
        self.limpar_marcadores()

    def _limpar_atores_da_vista(self, view):
        renderer = view.renderer
        actors = renderer.GetActors()
        actors.InitTraversal()
        to_remove = [actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
        for actor in to_remove: renderer.RemoveActor(actor)

    def _on_click_a(self, obj, event):
        x, y = obj.GetEventPosition()
        self.picker_a.Pick(x, y, 0, self.view_a.renderer)
        pos = self.picker_a.GetPickPosition()
        if any(pos):
            self.pontos_a.append(pos)
            self._desenhar_ponto(self.view_a, pos, (1, 0, 0))
            self.pontoAdicionado.emit("A", list(pos))

    def _on_click_b(self, obj, event):
        x, y = obj.GetEventPosition()
        self.picker_b.Pick(x, y, 0, self.view_b.renderer)
        pos = self.picker_b.GetPickPosition()
        if any(pos):
            self.pontos_b.append(pos)
            self._desenhar_ponto(self.view_b, pos, (0, 1, 0))
            self.pontoAdicionado.emit("B", list(pos))

    def _desenhar_ponto(self, view, pos, cor):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(pos)
        sphere.SetRadius(self.current_point_size)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(cor)
        setattr(actor, "is_marker", True)
        view.renderer.AddActor(actor)
        view.render()

    def limpar_marcadores(self):
        self.pontos_a = []
        self.pontos_b = []
        for view in [self.view_a, self.view_b]:
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            to_remove = []
            for _ in range(actors.GetNumberOfItems()):
                a = actors.GetNextActor()
                if getattr(a, "is_marker", False): to_remove.append(a)
            for a in to_remove: view.renderer.RemoveActor(a)
            view.render()

    def get_points_a(self):
        return self.pontos_a

    def get_points_b(self):
        return self.pontos_b


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    registration_widget = WindowRegistration()
    window.setCentralWidget(registration_widget)
    window.show()
    sys.exit(app.exec())