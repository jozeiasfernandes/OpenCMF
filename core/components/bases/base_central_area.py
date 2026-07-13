import vtk
from PySide6 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.scene.events.scene_events import SceneEvents
from core.components.bases.base_component import BaseComponent


class CentralAreaBase(BaseComponent):
    cena_atualizada = QtCore.Signal()

    def __init__(self, context, titulo="Central", cor_identificacao="#FFFFFF", usar_vtk=True, parent=None):

        super().__init__(context=context, parent=parent)
        self.titulo = titulo
        self.cor_id = cor_identificacao
        self.usar_vtk = usar_vtk
        self.vtkWidget = None
        self.renderer = vtk.vtkRenderer()  # Inicializado aqui


    def setup_component(self):
        """Implementação do contrato da BaseComponent"""
        self._setup_base_ui()
        self._conectar_sinais_scene()
        self._is_loaded = True

    def get_ui(self):
        return self

    def _setup_base_ui(self):
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        if self.usar_vtk:
            self.vtkWidget = QVTKRenderWindowInteractor(self)
            style = vtk.vtkInteractorStyleImage() if "3D" not in self.titulo else vtk.vtkInteractorStyleTrackballCamera()
            self.vtkWidget.SetInteractorStyle(style)
            self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

            self.indicator = QtWidgets.QLabel(self.titulo, self.vtkWidget)
            self.indicator.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
            self.layout_principal.addWidget(self.vtkWidget, stretch=1)


    def _conectar_sinais_scene(self):

        if self.scene_manager and hasattr(self.scene_manager, 'events'):
            bus = self.scene_manager.events
            bus.subscribe(SceneEvents.OBJECT_ADDED, self._on_scene_changed)


    def dispose(self):
        """Limpeza necessária para evitar leaks e crashes do VTK"""
        if self.scene_manager and self.scene_manager.events:
            self.scene_manager.events.unsubscribe(SceneEvents.OBJECT_ADDED, self._on_scene_changed)

        if self.vtkWidget:
            self.vtkWidget.Finalize()
        super().dispose()