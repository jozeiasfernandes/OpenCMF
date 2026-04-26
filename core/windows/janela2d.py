from PySide6 import QtWidgets, QtCore, QtGui
from core.windows.janelas import JanelaBase


class Janela2D(JanelaBase):
    sliceChanged = QtCore.Signal(int)

    def __init__(self, titulo: str, cor: str, parent=None):
        super().__init__(titulo, cor, parent)
        self._setup_controles_especificos()
        self._configurar_interacao()

    def _setup_controles_especificos(self):
        self.combo_proj = QtWidgets.QComboBox()
        self.combo_proj.addItems(["Axial", "Coronal", "Sagital"])
        self.combo_proj.setFixedWidth(85)

        self.slider_corte = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_corte.setMinimum(0)
        self.slider_corte.setStyleSheet("""
            QSlider::handle:horizontal {
                background: #3ea6fa;
                width: 4px;
                border-radius: 4px;
            }
        """)

        self.lbl_mm = QtWidgets.QLabel("0.0 mm")
        self.lbl_mm.setFixedWidth(55)
        self.lbl_mm.setAlignment(QtCore.Qt.AlignCenter)

        # Adiciona na barra inferior herdada
        self.adicionar_controle(self.combo_proj)
        self.adicionar_controle(QtWidgets.QLabel("Corte:"))
        self.adicionar_controle(self.slider_corte)
        self.adicionar_controle(self.lbl_mm)

        # Conecta o movimento do slider ao sinal de saída
        self.slider_corte.valueChanged.connect(self.sliceChanged.emit)

    def _configurar_interacao(self):
        # Habilita eventos de scroll do mouse no widget VTK para navegar fatias
        self.vtkWidget.AddObserver("MouseWheelForwardEvent", self._vtk_wheel_event)
        self.vtkWidget.AddObserver("MouseWheelBackwardEvent", self._vtk_wheel_event)

    def _vtk_wheel_event(self, obj, event):
        delta = 1 if event == "MouseWheelForwardEvent" else -1
        novo_valor = self.slider_corte.value() + delta
        self.slider_corte.setValue(novo_valor)