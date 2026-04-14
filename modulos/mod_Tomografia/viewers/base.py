import vtk
from PySide6 import QtWidgets, QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class JanelaBase(QtWidgets.QWidget):
    def __init__(self, nome: str, parent=None):
        super().__init__(parent)
        self.nome = nome
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vtkWidget.setStyleSheet("background-color: black; border: 1px solid #222;")

        self.indicator = QtWidgets.QLabel(nome, self.vtkWidget)
        self.indicator.setStyleSheet("color: #3ea6fa; background: rgba(0,0,0,150); font-weight: bold; padding: 2px;")
        self.indicator.move(0, 0)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setStyleSheet("background: #111; height: 10px;")
        self.slider.hide()

        self.layout_principal.addWidget(self.vtkWidget, stretch=1)
        self.layout_principal.addWidget(self.slider)