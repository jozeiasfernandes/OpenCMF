import vtk
from PySide6 import QtWidgets, QtCore
from typing import Dict, Optional
from .planar import Janela2D
from .volume import Janela3D


class VolumeViewerWidget(QtWidgets.QWidget):
    sliceChanged = QtCore.Signal(str, int)
    PLANOS = ["Axial", "Sagital", "Coronal"]
    DIM_MAP = {"Axial": 2, "Sagital": 0, "Coronal": 1}
    NORMALS = {"Axial": (0, 0, 1), "Sagital": (1, 0, 0), "Coronal": (0, 1, 0)}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vistas: Dict[str, QtWidgets.QWidget] = {}
        self.mappers_mpr: Dict[str, vtk.vtkImageResliceMapper] = {}
        self.volume_data: Optional[vtk.vtkImageData] = None
        self.opacity_function = vtk.vtkPiecewiseFunction()

        self.root_layout = QtWidgets.QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self._setup_ui()

    def _setup_ui(self):
        # Toolbar de Layout
        self.toolbar = QtWidgets.QToolBar()
        self.combo_layout = QtWidgets.QComboBox()
        self.combo_layout.addItems(["4 Quadrantes", "3D Destacado", "Apenas 3D"])
        self.combo_layout.currentTextChanged.connect(self.configurar_layout)
        self.toolbar.addWidget(QtWidgets.QLabel(" Layout: "))
        self.toolbar.addWidget(self.combo_layout)
        self.root_layout.addWidget(self.toolbar)

        # Grid de Visualização
        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(2)
        self.root_layout.addWidget(self.grid_container)

        # Inicializa as janelas especializadas
        for nome in self.PLANOS:
            pane = Janela2D(nome)
            pane.sliceChanged.connect(lambda v, n=nome: self.sliceChanged.emit(n, v))
            self.vistas[nome] = pane

        pane_3d = Janela3D("3D")
        pane_3d.thresholdChanged.connect(self.update_threshold)
        self.vistas["3D"] = pane_3d

        self.configurar_layout("4 Quadrantes")

    def configurar_layout(self, modo: str):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        for p in self.vistas.values(): p.hide()

        if modo == "4 Quadrantes":
            self.grid_layout.addWidget(self.vistas["Axial"], 0, 0)
            self.grid_layout.addWidget(self.vistas["Sagital"], 0, 1)
            self.grid_layout.addWidget(self.vistas["Coronal"], 1, 0)
            self.grid_layout.addWidget(self.vistas["3D"], 1, 1)
        elif modo == "Apenas 3D":
            self.grid_layout.addWidget(self.vistas["3D"], 0, 0)

        for i in range(self.grid_layout.count()):
            self.grid_layout.itemAt(i).widget().show()

    def update_threshold(self, value: int):
        self.opacity_function.RemoveAllPoints()
        self.opacity_function.AddPoint(value - 100, 0)
        self.opacity_function.AddPoint(value, 1)
        self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    # ... (Mantenha aqui as funções set_volume, update_slice e _configure_mpr_renderer que já tínhamos)

    def cleanup(self):
        for pane in self.vistas.values():
            pane.vtkWidget.GetRenderWindow().Finalize()
            pane.vtkWidget.TerminateApp()