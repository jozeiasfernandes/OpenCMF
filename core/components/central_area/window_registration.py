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
        if properties_panel:
            properties_panel.positionChanged.connect(lambda pos: self._apply_transform_change("position", pos))
            properties_panel.rotationChanged.connect(lambda rot: self._apply_transform_change("rotation", rot))
            properties_panel.scaleChanged.connect(lambda scl: self._apply_transform_change("scale", scl))
            properties_panel.colorChanged.connect(lambda col: self._apply_render_change("color", col))
            properties_panel.opacityChanged.connect(lambda op: self._apply_render_change("opacity", op))
            properties_panel.representationChanged.connect(lambda rep: self._apply_render_change("representation", rep))

    def remover_ultimo_marcador(self):
        for view, lista in [(self.view_a, self.pontos_a), (self.view_b, self.pontos_b)]:
            if not lista: continue
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            atores = [actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
            for actor in reversed(atores):
                if getattr(actor, "is_marker", False):
                    view.renderer.RemoveActor(actor)
                    lista.pop()
                    break
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
            controls_layout = QtWidgets.QHBoxLayout()

            combo_mesh = QtWidgets.QComboBox()
            combo_mesh.setPlaceholderText(f"Selecionar objeto...")

            combo_view = QtWidgets.QComboBox()
            combo_view.addItems(["Câmera Livre", "Frontal", "Posterior", "Direita", "Esquerda", "Superior", "Inferior"])
            combo_view.setFixedWidth(110)
            controls_layout.addWidget(combo_mesh, stretch=1)
            controls_layout.addWidget(combo_view)
            layout.addWidget(view, stretch=1)
            layout.addWidget(QtWidgets.QLabel("Objeto de Referência:" if side == "A" else "Objeto Móvel:"))
            layout.addLayout(controls_layout)
            setattr(self, f"view_{side.lower()}", view)
            setattr(self, f"combo_{side.lower()}", combo_mesh)
            setattr(self, f"combo_view_{side.lower()}", combo_view)
            combo_view.currentTextChanged.connect(lambda t, s=side: self._on_view_presets_changed(s, t))
            self.splitter.addWidget(container)
        self.main_layout.addWidget(self.splitter)
        self.combo_a.currentTextChanged.connect(lambda t: self._on_combo_changed("A", t))
        self.combo_b.currentTextChanged.connect(lambda t: self._on_combo_changed("B", t))
        QtCore.QTimer.singleShot(100, self._finalize_setup)

    def _on_view_presets_changed(self, side, view_name):
        if view_name == "Câmera Livre": return
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

    def _find_actor_by_id(self, view, identifier):
        actors = view.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if identifier in [getattr(actor, "id", None), getattr(actor, "name", None)]:
                return actor
        return None

    def _apply_transform_change(self, transform_type, values):
        for view_name, objetos in [("A", self.objetos_a), ("B", self.objetos_b)]:
            view = self.view_a if view_name == "A" else self.view_b
            for identifier in objetos.keys():
                actor = self._find_actor_by_id(view, identifier)
                if actor:
                    if transform_type == "position":
                        actor.SetPosition(values)
                    elif transform_type == "rotation":
                        actor.SetOrientation(values)
                    elif transform_type == "scale":
                        actor.SetScale(values)
            view.render()

    def _apply_render_change(self, render_type, value):
        for view_name, objetos in [("A", self.objetos_a), ("B", self.objetos_b)]:
            view = self.view_a if view_name == "A" else self.view_b
            for identifier in objetos.keys():
                actor = self._find_actor_by_id(view, identifier)
                if actor:
                    prop = actor.GetProperty()
                    if render_type == "color":
                        c = value
                        prop.SetColor(c.redF(), c.greenF(), c.blueF()) if isinstance(c,
                                                                                     QtGui.QColor) else prop.SetColor(c)
                    elif render_type == "opacity":
                        prop.SetOpacity(value)
                    elif render_type == "representation":
                        v = value.lower() if isinstance(value, str) else ""
                        if v == "surface":
                            prop.SetRepresentationToSurface()
                        elif v == "wireframe":
                            prop.SetRepresentationToWireframe()
            view.render()

    def adicionar_malha_vista_a(self, nome, polydata, obj_id=None):
        self._limpar_atores_da_vista(self.view_a)
        identifier = obj_id or nome
        self.objetos_a = {identifier: polydata}
        self.view_a.adicionar_objeto(identifier, polydata, cor=(0.7, 0.7, 0.9))
        self.view_a.render()

    def adicionar_malha_vista_b(self, nome, polydata, obj_id=None):
        self._limpar_atores_da_vista(self.view_b)
        identifier = obj_id or nome
        self.objetos_b = {identifier: polydata}
        self.view_b.adicionar_objeto(identifier, polydata, cor=(0.9, 0.9, 0.7))
        self.view_b.render()

    def _limpar_atores_da_vista(self, view):
        renderer = view.renderer
        actors = renderer.GetActors()
        actors.InitTraversal()
        to_remove = []
        for _ in range(actors.GetNumberOfItems()):
            a = actors.GetNextActor()
            if not getattr(a, "is_marker", False): to_remove.append(a)
        for a in to_remove: renderer.RemoveActor(a)

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

    def _finalize_setup(self):
        self.view_a.setup_interactors()
        self.view_b.setup_interactors()
        for v, h in [(self.view_a, self._on_click_a), (self.view_b, self._on_click_b)]:
            v.vtkWidget.GetRenderWindow().GetInteractor().AddObserver("LeftButtonPressEvent", h)
        self.reset_layout_vistas()

    def reset_layout_vistas(self):
        w = self.splitter.width()
        if w > 0: self.splitter.setSizes([w // 2, w // 2])
        self.view_a.render()
        self.view_b.render()

    def _on_click_a(self, obj, event):
        x, y = obj.GetEventPosition()
        p = vtk.vtkPointPicker()
        p.Pick(x, y, 0, self.view_a.renderer)
        pos = p.GetPickPosition()
        if any(pos):
            self.pontos_a.append(pos)
            self._desenhar_ponto(self.view_a, pos, (1, 0, 0))
            self.pontoAdicionado.emit("A", list(pos))

    def _on_click_b(self, obj, event):
        x, y = obj.GetEventPosition()
        p = vtk.vtkPointPicker()
        p.Pick(x, y, 0, self.view_b.renderer)
        pos = p.GetPickPosition()
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
        actor.is_marker = True
        view.renderer.AddActor(actor)
        view.render()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.resize(1024, 768)
    registration_widget = WindowRegistration()
    window.setCentralWidget(registration_widget)
    window.show()
    sys.exit(app.exec())