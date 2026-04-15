from PySide6 import QtWidgets, QtCore
from core.janelas.janelas import JanelaBase

class Janela2D(JanelaBase):
    sliceChanged = QtCore.Signal(int)

    def __init__(self, titulo, cor, parent=None):
        super().__init__(titulo, cor, parent)
        self._init_specific_widgets()
        self._connect_interactions()

    def _init_specific_widgets(self):
        self.combo_proj = QtWidgets.QComboBox()
        self.combo_proj.addItems(["Axial", "Coronal", "Sagital"])
        self.combo_proj.setFixedWidth(85)

        self.slider_corte = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_corte.setStyleSheet("""
            QSlider::handle:horizontal {
                background: #3EA6FA;
                width: 14px;
                border-radius: 7px;
            }
        """)

        self.lbl_mm = QtWidgets.QLabel("0.0 mm")
        self.lbl_mm.setFixedWidth(55)
        self.lbl_mm.setAlignment(QtCore.Qt.AlignCenter)

        self.adicionar_controle(self.combo_proj)
        self.adicionar_controle(QtWidgets.QLabel("Corte:"))
        self.adicionar_controle(self.slider_corte)
        self.adicionar_controle(self.lbl_mm)

        self.slider_corte.valueChanged.connect(self.sliceChanged.emit)

    def _connect_interactions(self):
        self.vtkWidget.AddObserver("MouseWheelForwardEvent", self._handle_vtk_wheel)
        self.vtkWidget.AddObserver("MouseWheelBackwardEvent", self._handle_vtk_wheel)

    def _handle_vtk_wheel(self, obj, event):
        delta = 1 if event == "MouseWheelForwardEvent" else -1
        current_value = self.slider_corte.value()
        self.slider_corte.setValue(current_value + delta)