#Base.py
import vtk
from PySide6 import QtWidgets, QtCore, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class JanelaBase(QtWidgets.QWidget):
    # Sinal para sincronizar brilho/contraste entre central_area
    windowLevelChanged = QtCore.Signal(float, float)

    def __init__(self, nome: str, parent=None):
        super().__init__(parent)
        self.nome = nome

        # 1. Estado do Window/Level e Mouse
        self.current_window = 1500.0
        self.current_level = 300.0
        self.ultimo_x = 0
        self.ultimo_y = 0
        self.is_wl_active = False

        # 2. Criação do widget VTK
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vtkWidget.setStyleSheet("background-color: black; border: 1px solid #222;")

        # 3. Criação do INDICADOR (O que causou o erro anterior)
        self.indicator = QtWidgets.QLabel(self.nome, self.vtkWidget)
        self.indicator.setStyleSheet("""
            color: #3ea6fa; 
            background: rgba(0,0,0,150); 
            font-weight: bold; 
            padding: 4px;
            border-radius: 2px;
        """)
        # Faz o label ignorar cliques para não atrapalhar o VTK
        self.indicator.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.indicator.move(5, 5)

        # 4. Configuração de Interação
        self.vtkWidget.SetInteractorStyle(None)
        self.vtkWidget.AddObserver("LeftButtonPressEvent", self._vtk_press_event)
        self.vtkWidget.AddObserver("MouseMoveEvent", self._vtk_move_event)
        self.vtkWidget.AddObserver("LeftButtonReleaseEvent", self._vtk_release_event)
        self.vtkWidget.AddObserver("MouseWheelForwardEvent", self._vtk_wheel_event)
        self.vtkWidget.AddObserver("MouseWheelBackwardEvent", self._vtk_wheel_event)

    # --- Pontes para eventos Qt ---

    def _vtk_press_event(self, interactor, event):
        self.is_wl_active = True
        pos = interactor.GetEventPosition()
        qt_pos = QtCore.QPointF(pos[0], self.vtkWidget.height() - pos[1])
        mouse_ev = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonPress, qt_pos,
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier
        )
        self.mousePressEvent(mouse_ev)

    def _vtk_move_event(self, interactor, event):
        if self.is_wl_active:
            pos = interactor.GetEventPosition()
            qt_pos = QtCore.QPointF(pos[0], self.vtkWidget.height() - pos[1])
            mouse_ev = QtGui.QMouseEvent(
                QtCore.QEvent.MouseMove, qt_pos,
                QtCore.Qt.NoButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier
            )
            self.mouseMoveEvent(mouse_ev)

    def _vtk_release_event(self, interactor, event):
        self.is_wl_active = False

    def _vtk_wheel_event(self, interactor, event):
        pass # Sobrescrito em CentralArea2D

    # --- Lógica de Movimentação (Window/Level) ---

    def mousePressEvent(self, event):
        if event:
            self.ultimo_x = event.position().x()
            self.ultimo_y = event.position().y()

    def mouseMoveEvent(self, event):
        if event and event.buttons() & QtCore.Qt.LeftButton:
            dx = event.position().x() - self.ultimo_x
            dy = event.position().y() - self.ultimo_y

            # Sensibilidade do ajuste
            self.current_window = max(1.0, self.current_window + dx * 2.0)
            self.current_level += dy * 2.0

            self.apply_window_level(self.current_window, self.current_level)

            self.ultimo_x = event.position().x()
            self.ultimo_y = event.position().y()

    def apply_window_level(self, window: float, level: float):
        self.current_window = window
        self.current_level = level
        self.windowLevelChanged.emit(window, level)