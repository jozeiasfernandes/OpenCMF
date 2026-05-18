import os
import sys
import vtk
from PySide6 import QtCore, QtWidgets, QtGui
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.scene.rendering.vtk_scene_renderer import VTKSceneRenderer
from core.scene.events.scene_events import SELECTION_CHANGED
from core.shortcut.shortcuts import get_shortcuts_by_scope, match_shortcut


os.environ["QT_API"] = "pyside6"

class Janela3DSurface(QtWidgets.QWidget):
    maximizeRequested = QtCore.Signal(bool)
    objectSelected = QtCore.Signal(str)

    COLOR_SELECTED = (1.0, 0.8, 0.0)
    COLOR_DEFAULT = (0.7, 0.7, 0.8)

    def __init__(self, nome, cor_borda, parent=None, scene_manager=None):
        super().__init__(parent)
        self.nome = nome
        self.cor_borda = cor_borda
        self.scene_manager = scene_manager
        self.is_maximized = False
        self._actor_base_colors: dict[str, tuple] = {}
        self._setup_ui()
        self._setup_vtk()
        self._connect_selection_manager()
        self.shortcuts = get_shortcuts_by_scope("view3d")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def _connect_selection_manager(self):
        if not self.scene_manager:
            return
        bus = getattr(self.scene_manager, "event_bus", None)
        if bus is None:
            return
        bus.subscribe(SELECTION_CHANGED, self._on_selection_changed)

    def _on_selection_changed(self, selected_ids: list[str]):
        actors = self.vtk_scene_renderer.get_actors()
        for obj_id, actor in actors.items():
            if getattr(actor, "is_marker", False):
                continue
            if obj_id in selected_ids:
                actor.GetProperty().SetColor(self.COLOR_SELECTED)
                actor.GetProperty().SetAmbient(0.3)
            else:
                base = self._actor_base_colors.get(obj_id, self.COLOR_DEFAULT)
                actor.GetProperty().SetColor(base)
                actor.GetProperty().SetAmbient(0.0)
        self.render()

    def _setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.setStyleSheet(f"background-color: {self.cor_borda};")
        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet("background-color: black; border: none;")
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        self.header = QtWidgets.QFrame()
        self.header.setFixedHeight(28)
        self.header.setStyleSheet("background-color: #1A1A1A;")
        self.header_layout = QtWidgets.QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 0, 5, 0)
        self.lbl_nome = QtWidgets.QLabel(self.nome.upper())
        self.lbl_nome.setStyleSheet(
            "color: white; font-size: 10px; font-weight: bold; border: none;"
        )
        self.btn_max = QtWidgets.QPushButton("▢")
        self.btn_max.setFixedSize(22, 22)
        self.btn_max.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_max.setStyleSheet(""" 
            QPushButton { 
                color: #888; border: none; font-size: 14px; 
            }
            QPushButton:hover { 
                color: white; background-color: #333; 
            } 
        """)
        self.btn_max.clicked.connect(self._handle_maximize)
        self.header_layout.addWidget(self.lbl_nome)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_max)
        self.vtkWidget = QVTKRenderWindowInteractor(self.container)
        self.container_layout.addWidget(self.header)
        self.container_layout.addWidget(self.vtkWidget)
        self.main_layout.addWidget(self.container)

    def _setup_vtk(self):
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.05, 0.05, 0.05)
        self.vtk_scene_renderer = VTKSceneRenderer(self.renderer)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtkWidget.GetRenderWindow().SetMultiSamples(8)
        self.picker = vtk.vtkPropPicker()

    def setup_interactors(self):
        self.vtkWidget.Initialize()
        style = vtk.vtkInteractorStyleTrackballCamera()
        style.AddObserver("LeftButtonPressEvent", self._on_left_click)
        self.vtkWidget.SetInteractorStyle(style)
        self.vtkWidget.Start()

    def _on_left_click(self, obj, event):
        x, y = self.vtkWidget.GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)
        actor = self.picker.GetActor()
        if actor and hasattr(actor, "id"):
            obj_id = actor.id
            self.objectSelected.emit(obj_id)
            if self.scene_manager:
                modifiers = QtWidgets.QApplication.keyboardModifiers()
                if modifiers & QtCore.Qt.ControlModifier:
                    self.scene_manager.selection.toggle(obj_id)
                else:
                    self.scene_manager.selection.select(obj_id, exclusive=True)
            else:
                if self.scene_manager:
                    self.scene_manager.selection.clear()
        obj.OnLeftButtonDown()

    def set_interactor_style(self, style):
        self.vtkWidget.SetInteractorStyle(style)
        self.render()

    def add_object(
        self,
        id_obj: str,
        polydata,
        cor: tuple = (0.7, 0.7, 0.8),
        opacidade: float = 1.0,
        nome_amigavel: str = "",
    ):
        self.vtk_scene_renderer.remove_actor(id_obj)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.id = id_obj
        actor.name = nome_amigavel
        actor.is_marker = False
        actor.PickableOn()
        actor.GetProperty().SetColor(cor)
        actor.GetProperty().SetOpacity(opacidade)
        self._actor_base_colors[id_obj] = cor
        self.vtk_scene_renderer.add_actor(id_obj, actor)
        if self.scene_manager and self.scene_manager.selection.is_selected(id_obj):
            actor.GetProperty().SetColor(self.COLOR_SELECTED)
            actor.GetProperty().SetAmbient(0.3)
        self.render()

    def del_object(self, id_obj: str):
        self.vtk_scene_renderer.remove_actor(id_obj)
        self._actor_base_colors.pop(id_obj, None)
        self.render()

    def render(self):
        if hasattr(self.vtkWidget, "GetRenderWindow"):
            self.vtkWidget.GetRenderWindow().Render()

    def reset_camera(self):
        self.renderer.ResetCamera()
        self.render()

    def _handle_maximize(self):
        self.is_maximized = not self.is_maximized
        self.btn_max.setText("❐" if self.is_maximized else "▢")
        self.maximizeRequested.emit(self.is_maximized)

    def keyPressEvent(self, event):
        action = match_shortcut(event, self.shortcuts)

        if action:
            self.execute_action(action)
            event.accept()
        else:
            super().keyPressEvent(event)

    def execute_action(self, action_id: str):
        # Mapeamento das visões 3D: (pos_x, pos_y, pos_z, view_up_x, view_up_y, view_up_z)
        view_maps = {
            "view3d.frontal": (0, -1, 0, 0, 0, 1),
            "view3d.right": (1, 0, 0, 0, 0, 1),
            "view3d.left": (-1, 0, 0, 0, 0, 1),
            "view3d.superior": (0, 0, 1, 0, -1, 0),
            "view3d.inferior": (0, 0, -1, 0, 1, 0),
        }

        # 1. Alteração de Câmera (Visões Padrão)
        if action_id in view_maps:
            cam = self.renderer.GetActiveCamera()
            coords = view_maps[action_id]

            # Correção: Desempacotamento explícito usando '*' para compatibilidade com VTK C++
            cam.SetPosition(*coords[:3])
            cam.SetViewUp(*coords[3:])
            cam.SetFocalPoint(0, 0, 0)

            self.renderer.ResetCamera()
            self.render()

        # 2. Projeção Ortogonal / Perspectiva
        elif action_id == "view3d.orthogonal":
            cam = self.renderer.GetActiveCamera()
            cam.SetParallelProjection(not cam.GetParallelProjection())
            self.render()

        # 3. Deleção de Objetos Selecionados
        elif action_id == "view3d.delete_object":
            if self.scene_manager and self.scene_manager.selection.selected_ids:
                # Criação de uma lista estática e isolada dos IDs para evitar conflito de iteração
                to_delete = list(self.scene_manager.selection.selected_ids)

                # Limpa a seleção antes do processamento para blindar a UI contra glitches
                self.scene_manager.selection.clear()

                for obj_id in to_delete:
                    self.scene_manager.remove_object(obj_id)

                self.render()

        # 4. Isolamento Anatômico e Foco
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

            # Varredura segura nos atores ativos do renderizador VTK
            actors = self.vtk_scene_renderer.get_actors()
            for obj_id, actor in actors.items():
                actor_name = getattr(actor, "name", "") or ""
                if any(kw in obj_id.lower() or kw in actor_name.lower() for kw in keywords):
                    target_actor = actor
                    target_id = obj_id
                    break

            # Aplica a seleção exclusiva e ajusta o zoom da câmera no objeto encontrado
            if target_id and self.scene_manager:
                self.scene_manager.selection.select(target_id, exclusive=True)

            if target_actor:
                self.renderer.ResetCamera(target_actor.GetBounds())
                self.render()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    janela_teste = Janela3DSurface("Vista de Superfície", "#00AAFF")
    janela_teste.resize(800, 600)
    janela_teste.show()
    janela_teste.setup_interactors()
    sphere = vtk.vtkSphereSource()
    sphere.Update()
    janela_teste.add_object("esfera_teste", sphere.GetOutput(), cor=(0.2, 0.6, 1.0))
    janela_teste.reset_camera()
    sys.exit(app.exec())