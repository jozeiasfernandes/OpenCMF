import vtk
from PySide6 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.scene.events.scene_events import SceneEvents


class CentralAreaBase(QtWidgets.QWidget):
    cena_atualizada = QtCore.Signal()

    def __init__(self, titulo, cor_identificacao, scene_manager=None, parent=None):
        super().__init__(parent)
        self.titulo = titulo
        self.cor_id = cor_identificacao
        self.scene_manager = scene_manager

        self._setup_base_ui()
        self._conectar_sinais_scene()

    def _setup_base_ui(self):
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        self.vtkWidget = QVTKRenderWindowInteractor(self)

        style = vtk.vtkInteractorStyleImage() if "3D" not in self.titulo else vtk.vtkInteractorStyleTrackballCamera()
        self.vtkWidget.SetInteractorStyle(style)

        self.indicator = QtWidgets.QLabel(self.titulo, self.vtkWidget)
        self.indicator.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.barra_inferior = QtWidgets.QFrame()
        self.barra_inferior.setFixedHeight(30)
        self.layout_barra = QtWidgets.QHBoxLayout(self.barra_inferior)

        self.layout_principal.addWidget(self.vtkWidget, stretch=1)
        self.layout_principal.addWidget(self.barra_inferior)

    def _conectar_sinais_scene(self):
        if self.scene_manager and self.scene_manager.events:
            bus = self.scene_manager.events
            bus.subscribe(SceneEvents.OBJECT_ADDED, self._on_scene_changed)
            bus.subscribe(SceneEvents.OBJECT_REMOVED, self._on_scene_changed)
            bus.subscribe(SceneEvents.OBJECT_UPDATED, self._on_scene_changed)
            bus.subscribe(SceneEvents.SELECTION_CHANGED, self._on_selection_changed)

    def _on_scene_changed(self, **kwargs):
        self.vtkWidget.GetRenderWindow().Render()
        self.cena_atualizada.emit()

    def _on_selection_changed(self, selected_ids):
        pass

    def showEvent(self, event):
        super().showEvent(event)
        self.vtkWidget.Initialize()
        if hasattr(self, 'renderer'):
            self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'indicator'):
            self.indicator.move(5, 5)

    def adicionar_controle(self, widget):
        self.layout_barra.addWidget(widget)

    def cleanup(self):
        if self.scene_manager and self.scene_manager.events:
            bus = self.scene_manager.events
            bus.unsubscribe(SceneEvents.OBJECT_ADDED, self._on_scene_changed)
            bus.unsubscribe(SceneEvents.OBJECT_REMOVED, self._on_scene_changed)
            bus.unsubscribe(SceneEvents.OBJECT_UPDATED, self._on_scene_changed)
            bus.unsubscribe(SceneEvents.SELECTION_CHANGED, self._on_selection_changed)