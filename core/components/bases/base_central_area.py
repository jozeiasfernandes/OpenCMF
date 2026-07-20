import vtk
from PySide6 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.scene.events.scene_events import SceneEvents
from core.components.bases.base_component import BaseComponent


class CentralAreaBase(QtWidgets.QWidget):
    """
    Classe base para áreas centrais.
    Herda de QWidget e utiliza BaseComponent por composição para injeção de dependência e ciclo de vida.
    """
    cena_atualizada = QtCore.Signal()

    def __init__(self, context, title="Central", cor_identificacao="#FFFFFF", usar_vtk=True, parent=None):
        super().__init__(parent)

        # Composição com BaseComponent para herdar o contrato de injeção de contexto
        self._logic = BaseComponent(context=context, parent=self)

        self.title = title
        self.cor_id = cor_identificacao
        self.usar_vtk = usar_vtk
        self.vtkWidget = None
        self.renderer = vtk.vtkRenderer()
        self.layout_principal = None
        self.indicator = None
        self.is_maximized = False

        self._setup_base_ui()

    @property
    def context(self):
        """Retorna o contexto atual injetado."""
        return self._logic.context if hasattr(self, '_logic') else None

    @property
    def scene_manager(self):
        """Retorna o scene_manager de forma segura através do BaseComponent."""
        return self._logic.scene_manager if hasattr(self, '_logic') else None

    @property
    def tool_manager(self):
        """Retorna o tool_manager de forma segura através do BaseComponent."""
        return self._logic.tool_manager if hasattr(self, '_logic') else None

    @property
    def event_bus(self):
        """Retorna o barramento de eventos seguro através do BaseComponent ou scene_manager."""
        if hasattr(self._logic, 'event_bus') and self._logic.event_bus:
            return self._logic.event_bus
        if self.scene_manager and hasattr(self.scene_manager, 'events'):
            return self.scene_manager.events
        return None

    def setup_component(self):
        """Implementação do contrato de inicialização."""
        # Atualizado para utilizar o atributo '_loaded' da nova BaseComponent
        if self._logic._loaded:
            return

        # Conectar sinais da cena
        self._conectar_sinais_scene()

        # Chamar setup_ui das classes filhas
        self.setup_ui()

        self._logic._loaded = True

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
            style = vtk.vtkInteractorStyleImage() if "3D" not in self.title else vtk.vtkInteractorStyleTrackballCamera()
            self.vtkWidget.SetInteractorStyle(style)
            self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

            self.indicator = QtWidgets.QLabel(self.title, self.vtkWidget)
            self.indicator.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
            self.indicator.setStyleSheet("color: white; background-color: rgba(0,0,0,0.5); padding: 5px;")

            self.layout_principal.addWidget(self.vtkWidget, stretch=1)

    def _conectar_sinais_scene(self):
        """Conecta sinais do barramento de eventos."""
        bus = self.event_bus
        if bus and hasattr(bus, 'subscribe'):
            bus.subscribe(SceneEvents.OBJECT_ADDED, self._on_scene_changed)

    def _on_scene_equal_changed(self, **kwargs):
        pass

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
        bus = self.event_bus
        if bus and hasattr(bus, 'unsubscribe'):
            try:
                bus.unsubscribe(SceneEvents.OBJECT_ADDED, self._on_scene_changed)
            except Exception:
                pass

        if self.vtkWidget:
            try:
                self.vtkWidget.Finalize()
            except Exception:
                pass

        if hasattr(self, '_logic'):
            self._logic.dispose()

    def adicionar_controle(self, widget: QtWidgets.QWidget):
        self.area_controles.addWidget(widget)