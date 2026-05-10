from PySide6 import QtWidgets, QtCore
import vtk
import sys
from core.components.central_area.windows_3d import Janela3DSurface


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
            properties_panel.edgeVisibilityChanged.connect(lambda vis: self._apply_render_change("edge_visibility", vis))

    def _apply_transform_change(self, transform_type: str, values: list) -> None:
        for view_name, objetos in [("A", self.objetos_a), ("B", self.objetos_b)]:
            for nome_objeto in objetos.keys():
                self._apply_transform_to_object(view_name, nome_objeto, transform_type, values)

    def _apply_render_change(self, render_type: str, value) -> None:
        for view_name, objetos in [("A", self.objetos_a), ("B", self.objetos_b)]:
            for nome_objeto in objetos.keys():
                self._apply_render_to_object(view_name, nome_objeto, render_type, value)

    def _apply_transform_to_object(self, view_name: str, object_name: str, transform_type: str, values: list) -> None:
        view = self.view_a if view_name == "A" else self.view_b
        actors = view.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if hasattr(actor, "name") and actor.name == object_name:
                if transform_type == "position":
                    actor.SetPosition(values)
                elif transform_type == "rotation":
                    actor.SetOrientation(values)
                elif transform_type == "scale":
                    actor.SetScale(values)
                break
        view.render()

    def _apply_render_to_object(self, view_name: str, object_name: str, render_type: str, value) -> None:
        view = self.view_a if view_name == "A" else self.view_b
        actors = view.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if hasattr(actor, "name") and actor.name == object_name:
                prop = actor.GetProperty()
                if render_type == "color":
                    prop.SetColor(value)
                elif render_type == "opacity":
                    prop.SetOpacity(value)
                elif render_type == "representation":
                    if value.lower() == "surface":
                        prop.SetRepresentationToSurface()
                    elif value.lower() == "wireframe":
                        prop.SetRepresentationToWireframe()
                    elif value.lower() == "points":
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
                break
        view.render()

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setMinimumSize(0, 0)
        self.splitter.setChildrenCollapsible(True)

        self.container_a = QtWidgets.QWidget()
        self.container_a.setMinimumSize(0, 0)
        self.container_a.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        layout_a = QtWidgets.QVBoxLayout(self.container_a)
        layout_a.setContentsMargins(4, 4, 4, 4)
        layout_a.setSpacing(2)

        self.view_a = Janela3DSurface("Vista A", "#00AAFF")
        self.view_a.setMinimumSize(0, 0)          # impede travamento ao redimensionar
        self.view_a.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        self.combo_a = QtWidgets.QComboBox()
        self.combo_a.setPlaceholderText("Selecionar objeto Vista A...")
        layout_a.addWidget(self.view_a, stretch=1)
        layout_a.addWidget(QtWidgets.QLabel("Objeto de Referência (Fixo):"))
        layout_a.addWidget(self.combo_a)

        self.container_b = QtWidgets.QWidget()
        self.container_b.setMinimumSize(0, 0)
        self.container_b.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        layout_b = QtWidgets.QVBoxLayout(self.container_b)
        layout_b.setContentsMargins(4, 4, 4, 4)
        layout_b.setSpacing(2)

        self.view_b = Janela3DSurface("Vista B", "#555555")
        self.view_b.setMinimumSize(0, 0)          # impede travamento ao redimensionar
        self.view_b.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        self.combo_b = QtWidgets.QComboBox()
        self.combo_b.setPlaceholderText("Selecionar objeto Vista B...")
        layout_b.addWidget(self.view_b, stretch=1)
        layout_b.addWidget(QtWidgets.QLabel("Objeto Móvel (A alinhar):"))
        layout_b.addWidget(self.combo_b)

        self.splitter.addWidget(self.container_a)
        self.splitter.addWidget(self.container_b)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.main_layout.addWidget(self.splitter)

        self.combo_a.currentTextChanged.connect(lambda texto: self._on_combo_changed("A", texto))
        self.combo_b.currentTextChanged.connect(lambda texto: self._on_combo_changed("B", texto))

        QtCore.QTimer.singleShot(100, self._finalize_setup)

    def _finalize_setup(self):
        self.setup_interactors()
        self.reset_layout_vistas()

    def setup_interactors(self):
        self.view_a.setup_interactors()
        self.view_b.setup_interactors()
        for view, picker_attr, click_handler in [
            (self.view_a, 'picker_a', self._on_click_a),
            (self.view_b, 'picker_b', self._on_click_b)
        ]:
            interactor = view.vtkWidget.GetRenderWindow().GetInteractor()
            picker = vtk.vtkPointPicker()
            setattr(self, picker_attr, picker)
            interactor.SetPicker(picker)
            interactor.AddObserver("LeftButtonPressEvent", click_handler)

    def reset_layout_vistas(self):
        total_width = self.splitter.width()
        if total_width > 0:
            self.splitter.setSizes([total_width // 2, total_width // 2])
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
            if current in nomes_objetos:
                combo.setCurrentText(current)
            combo.blockSignals(False)

    def _on_combo_changed(self, vista_id, nome_objeto):
        if nome_objeto:
            self.requisitarCarregamentoObjeto.emit(vista_id, nome_objeto)

    # --- Malhas ---

    def adicionar_malha_vista_a(self, nome, polydata):
        self._limpar_atores_da_vista(self.view_a)
        self.objetos_a = {nome: polydata}
        self.view_a.adicionar_objeto(nome, polydata, cor=(0.7, 0.7, 0.9))
        if self.combo_a.currentText() != nome:
            self.combo_a.blockSignals(True)
            self.combo_a.setCurrentText(nome)
            self.combo_a.blockSignals(False)
        self.view_a.reset_camera()
        self.view_a.render()

    def adicionar_malha_vista_b(self, nome, polydata):
        self._limpar_atores_da_vista(self.view_b)
        self.objetos_b = {nome: polydata}
        self.view_b.adicionar_objeto(nome, polydata, cor=(0.9, 0.9, 0.7))
        if self.combo_b.currentText() != nome:
            self.combo_b.blockSignals(True)
            self.combo_b.setCurrentText(nome)
            self.combo_b.blockSignals(False)
        self.view_b.reset_camera()
        self.view_b.render()

    def remover_objeto(self, nome):
        try:
            self.view_a.remover_objeto(nome)
            self.view_b.remover_objeto(nome)
        except AttributeError:
            pass
        if nome in self.objetos_a:
            del self.objetos_a[nome]
        if nome in self.objetos_b:
            del self.objetos_b[nome]
        self.view_a.render()
        self.view_b.render()

    def set_objeto_opacidade(self, nome, valor):
        for view in [self.view_a, self.view_b]:
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            for _ in range(actors.GetNumberOfItems()):
                actor = actors.GetNextActor()
                if hasattr(actor, "name") and actor.name == nome:
                    actor.GetProperty().SetOpacity(valor)
            view.render()

    def set_objeto_cor(self, nome, cor_rgb):
        for view in [self.view_a, self.view_b]:
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            for _ in range(actors.GetNumberOfItems()):
                actor = actors.GetNextActor()
                if hasattr(actor, "name") and actor.name == nome:
                    actor.GetProperty().SetColor(cor_rgb)
            view.render()

    def limpar_vistas_total(self):
        self._limpar_atores_da_vista(self.view_a)
        self._limpar_atores_da_vista(self.view_b)
        self.objetos_a.clear()
        self.objetos_b.clear()
        self.limpar_marcadores()
        self.view_a.render()
        self.view_b.render()

    def _limpar_atores_da_vista(self, view):
        renderer = view.renderer
        actors = renderer.GetActors()
        actors.InitTraversal()
        atores_para_remover = [actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
        for actor in atores_para_remover:
            renderer.RemoveActor(actor)

    # --- Pontos ---

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
        actor.SetObjectName("marcador_ponto")
        view.renderer.AddActor(actor)
        view.render()

    def remover_ultimo_marcador(self):
        for view, lista in [(self.view_a, self.pontos_a), (self.view_b, self.pontos_b)]:
            if not lista:
                continue
            actors = list(view.renderer.GetActors())
            for actor in reversed(actors):
                if hasattr(actor, "GetObjectName") and actor.GetObjectName() == "marcador_ponto":
                    view.renderer.RemoveActor(actor)
                    lista.pop()
                    break
            view.render()

    def limpar_marcadores(self):
        self.pontos_a = []
        self.pontos_b = []
        for view in [self.view_a, self.view_b]:
            actors = list(view.renderer.GetActors())
            for actor in actors:
                if hasattr(actor, "GetObjectName") and actor.GetObjectName() == "marcador_ponto":
                    view.renderer.RemoveActor(actor)
            view.render()

    def set_ponto_raio(self, size: float):
        self.current_point_size = size
        for view in [self.view_a, self.view_b]:
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            for _ in range(actors.GetNumberOfItems()):
                actor = actors.GetNextActor()
                if hasattr(actor, "GetObjectName") and actor.GetObjectName() == "marcador_ponto":
                    mapper = actor.GetMapper()
                    if mapper:
                        source = mapper.GetInputAlgorithm()
                        if isinstance(source, vtk.vtkSphereSource):
                            source.SetRadius(size)
            view.render()

    def get_points_a(self):
        return self.pontos_a

    def get_points_b(self):
        return self.pontos_b


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.resize(1024, 768)
    registration_widget = WindowRegistration()
    window.setCentralWidget(registration_widget)
    window.show()
    sys.exit(app.exec())