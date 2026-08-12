import vtk
from PySide6 import QtWidgets, QtCore, QtGui

# Scene
from application.scene.events.scene_events import SceneEvents

# Components
from core.components.bases.base_component import BaseComponent
from core.components.bases.base_tool.viewport_interaction_controller import ViewportInteractionController

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
fmt = QtGui.QSurfaceFormat()
fmt.setRenderableType(QtGui.QSurfaceFormat.OpenGL)
fmt.setVersion(3, 2)
fmt.setProfile(QtGui.QSurfaceFormat.CoreProfile)
QtGui.QSurfaceFormat.setDefaultFormat(fmt)


class CentralAreaBase(QtWidgets.QWidget):
    """
    Classe base para áreas centrais.
    Herda de QWidget e utiliza BaseComponent por composição para injeção de dependência e ciclo de vida.
    """
    cena_atualizada = QtCore.Signal()

    def __init__(self, context=None, title="Central", cor_identificacao="#FFFFFF", usar_vtk=True, parent=None):
        super().__init__(parent)

        # Composição com BaseComponent para herdar o contrato de injeção de contexto e ciclo de vida
        self._logic = BaseComponent(context=context, parent=self)

        self.title = title
        self.cor_id = cor_identificacao
        self.usar_vtk = usar_vtk
        self.vtkWidget = None
        self.renderer = vtk.vtkRenderer()
        self.layout_principal = None
        self.indicator = None
        self.is_maximized = False
        self.interaction_controller = None  # Controlador de interações com o ToolManager

        # Garante política de expansão correta para evitar cortes ou sobreposições no layout pai
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._setup_base_ui()

    # ==========================================
    # PROPRIEDADES E GETTERS
    # ==========================================

    @property
    def context(self):
        """Retorna o contexto atual injetado."""
        return self._logic.context if hasattr(self, '_logic') else None

    @context.setter
    def context(self, new_context):
        """Permite redefinir o contexto repassando para o componente lógico."""
        if hasattr(self, '_logic'):
            self._logic.set_context(new_context)

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

    def get_ui(self):
        return self

    # ==========================================
    # CONFIGURAÇÃO DE UI E COMPONENTES
    # ==========================================

    def setup_component(self):
        """Implementação do contrato de inicialização alinhada ao BaseComponent."""
        if self._logic._loaded:
            return

        # Conectar sinais da cena
        self._conectar_sinais_scene()

        # Chamar setup_ui das classes filhas
        self.setup_ui()

        # Sincroniza o estado de carregamento no componente lógico de composição
        self._logic._loaded = True

    def setup_ui(self):
        """Método para ser sobrescrito pelas classes filhas."""
        pass

    def _setup_base_ui(self):
        """Configura a UI base de forma limpa e sem sobreposições de layout."""
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

            # Assegura política expansiva para o widget VTK
            self.vtkWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

            self.indicator = QtWidgets.QLabel(self.title, self.vtkWidget)
            self.indicator.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
            self.indicator.setStyleSheet("colors: white; background-colors: rgba(0,0,0,0.5); padding: 5px;")

            self.layout_principal.addWidget(self.vtkWidget, stretch=1)

            # Inicializa o controlador de interações se o tool_manager estiver disponível no contexto
            if self.tool_manager:
                self.interaction_controller = ViewportInteractionController(
                    vtk_widget=self.vtkWidget,
                    tool_manager=self.tool_manager
                )

    def add_control(self, widget: QtWidgets.QWidget):
        self.area_controles.addWidget(widget)

    # ==========================================
    # GERENCIAMENTO DE SINAIS E EVENTOS
    # ==========================================

    def _conectar_sinais_scene(self):
        """Conecta sinais do barramento de eventos."""
        bus = self.event_bus
        if bus and hasattr(bus, 'subscribe'):
            try:
                bus.subscribe(SceneEvents.OBJECT_ADDED, self._on_scene_changed)
            except Exception:
                pass

    def _on_scene_changed(self, **kwargs):
        """Callback quando a cena muda."""
        self.cena_atualizada.emit()
        self.render()

    def resizeEvent(self, event):
        """Força a limpeza e atualização imediata do renderizador VTK e do widget ao redimensionar."""
        super().resizeEvent(event)
        if self.vtkWidget:
            try:
                # Força o reajuste da janela de renderização do VTK
                window = self.vtkWidget.GetRenderWindow()
                if window:
                    window.Render()
                self.vtkWidget.update()
                self.vtkWidget.repaint()
            except Exception:
                pass
        self.update()
        self.repaint()

    # ==========================================
    # RENDERIZAÇÃO E CICLO DE ENCERRAMENTO
    # ==========================================

    def render(self):
        """Renderiza a cena."""
        if self.vtkWidget and self.vtkWidget.GetRenderWindow():
            self.vtkWidget.GetRenderWindow().Render()

    def dispose(self):
        """Limpeza necessária para evitar leaks e crashes do VTK e do BaseComponent."""
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