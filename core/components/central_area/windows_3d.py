import vtk
import sys
import os
os.environ["QT_API"] = "pyside6"

from PySide6 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class Janela3DSurface(QtWidgets.QWidget):
    maximizeRequested = QtCore.Signal(bool)
    pointPicked = QtCore.Signal(str, tuple)

    def __init__(self, nome, cor_borda, parent=None):
        super().__init__(parent)
        self.nome = nome
        self.cor_borda = cor_borda
        self.is_maximized = False
        self.atores_malha = {}

        self._setup_ui()
        self._setup_vtk()

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
        self.lbl_nome.setStyleSheet("color: white; font-size: 10px; font-weight: bold; border: none;")

        self.btn_max = QtWidgets.QPushButton("▢")
        self.btn_max.setFixedSize(22, 22)
        self.btn_max.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_max.setStyleSheet("""
            QPushButton { color: #888; border: none; font-size: 14px; }
            QPushButton:hover { color: white; background-color: #333; }
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
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtkWidget.GetRenderWindow().SetMultiSamples(8)

    def setup_interactors(self):
        self.vtkWidget.Initialize()
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.vtkWidget.SetInteractorStyle(style)
        self.vtkWidget.Start()

    def adicionar_objeto(self, id_obj, polydata, cor=(0.7, 0.7, 0.8), opacidade=1.0, nome_amigavel=""):
        if id_obj in self.atores_malha:
            self.renderer.RemoveActor(self.atores_malha[id_obj])

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        actor.id = id_obj
        actor.name = nome_amigavel

        actor.GetProperty().SetColor(cor)
        actor.GetProperty().SetOpacity(opacidade)

    def remover_objeto(self, id_obj):
        if id_obj in self.atores_malha:
            self.renderer.RemoveActor(self.atores_malha[id_obj])
            del self.atores_malha[id_obj]
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




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    janela_teste = Janela3DSurface("Vista de Superfície", "#00AAFF")
    janela_teste.resize(800, 600)
    janela_teste.show()

    janela_teste.setup_interactors()


    sphere = vtk.vtkSphereSource()
    sphere.SetThetaResolution(30)
    sphere.SetPhiResolution(30)
    sphere.Update()

    janela_teste.adicionar_objeto("esfera_teste", sphere.GetOutput(), cor=(0.2, 0.6, 1.0))
    janela_teste.reset_camera()

    sys.exit(app.exec())