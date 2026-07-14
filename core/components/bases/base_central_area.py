import vtk
from PySide6 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.scene.events.scene_events import SceneEvents
from core.components.bases.base_component import BaseComponent


class CentralAreaBase(QtWidgets.QWidget):
    """
    Classe base para áreas centrais.
    Herda de QWidget e usa BaseComponent por composição.
    """
    cena_atualizada = QtCore.Signal()
    def __init__(self, context, titulo="Central", cor_identificacao="#FFFFFF", usar_vtk=True, parent=None):
        super().__init__(parent)
        self._logic = BaseComponent(context=context, parent=self)
        self.titulo = titulo
        self.cor_id = cor_identificacao
        self.usar_vtk = usar_vtk
        self.vtkWidget = None
        self.renderer = vtk.vtkRenderer()
        self.layout_principal = None
        self.indicator = None
        self._is_loaded = False
        self.is_maximized = False
        self._setup_base_ui()

    @property
    def scene_manager(self):
        """Retorna o scene_manager do contexto."""
        return self._logic.scene_manager if hasattr(self, '_logic') else None

    @property
    def event_bus(self):
        """Retorna o event_bus do scene_manager."""
        return self.scene_manager.events if self.scene_manager else None

    def setup_component(self):
        """Implementação do contrato da BaseComponent."""
        if self._is_loaded:
            return

        # Conectar sinais da cena
        self._conectar_sinais_scene()

        # Chamar setup_ui das classes filhas
        self.setup_ui()

        self._is_loaded = True

    def get_ui(self):
        return self

    def _setup_base_ui(self):
        """Configura a UI base."""
        if self.layout_principal is None:
            self.layout_principal = QtWidgets.QVBoxLayout(self)
            self.layout_principal.setContentsMargins(0, 0, 0, 0)
            self.layout_principal.setSpacing(0)
            self.area_controles = QtWidgets.QHBoxLayout()
            self.area_controles.setContentsMargins(5, 5, 5, 5)
            self.layout_principal.addLayout(self.area_controles)

        if self.usar_vtk and self.vtkWidget is None:
            self.vtkWidget = QVTKRenderWindowInteractor(self)
            style = vtk.vtkInteractorStyleImage() if "3D" not in self.titulo else vtk.vtkInteractorStyleTrackballCamera()
            self.vtkWidget.SetInteractorStyle(style)
            self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

            self.indicator = QtWidgets.QLabel(self.titulo, self.vtkWidget)
            self.indicator.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
            self.indicator.setStyleSheet("color: white; background-color: rgba(0,0,0,0.5); padding: 5px;")

            self.layout_principal.addWidget(self.vtkWidget, stretch=1)

    def _conectar_sinais_scene(self):
        """Conecta sinais do scene_manager."""
        if self.scene_manager and hasattr(self.scene_manager, 'events'):
            bus = self.scene_manager.events
            bus.subscribe(SceneEvents.OBJECT_ADDED, self._on_scene_changed)

    def _on_scene_changed(self, **kwargs):
        """Callback quando a cena muda."""
        self.cena_atualizada.emit()
        self.render()

    def render(self):
        """Renderiza a cena."""
        if self.vtkWidget and self.vtkWidget.GetRenderWindow():
            self.vtkWidget.GetRenderWindow().Render()

    def setup_ui(self):
        """Método para ser sobrescrito pelas classes filhas."""
        pass

    def dispose(self):
        """Limpeza necessária para evitar leaks e crashes do VTK."""
        if self.scene_manager and self.scene_manager.events:
            self.scene_manager.events.unsubscribe(SceneEvents.OBJECT_ADDED, self._on_scene_changed)

        if self.vtkWidget:
            self.vtkWidget.Finalize()

        if hasattr(self, '_logic'):
            self._logic.dispose()

        self._is_loaded = False

    def adicionar_controle(self, widget: QtWidgets.QWidget):
        self.area_controles.addWidget(widget)