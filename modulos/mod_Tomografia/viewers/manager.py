import vtk
import os
from PySide6 import QtWidgets, QtCore, QtGui
from typing import Dict, Optional

# Importações relativas (certifique-se que esses arquivos existem na mesma pasta)
from .planar import Janela2D
from .volume import Janela3D


class VolumeViewerWidget(QtWidgets.QWidget):
    """
    Gerenciador das vistas MPR (2D) e Volume Rendering (3D).
    """
    # Sinais para comunicação com o Modulo (Controller)
    sliceChanged = QtCore.Signal(str, int)
    windowLevelChanged = QtCore.Signal(float, float)

    PLANOS = ["Axial", "Sagital", "Coronal"]
    DIM_MAP = {"Axial": 2, "Sagital": 0, "Coronal": 1}
    NORMALS = {"Axial": (0, 0, 1), "Sagital": (1, 0, 0), "Coronal": (0, 1, 0)}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vistas: Dict[str, QtWidgets.QWidget] = {}
        self.mappers_mpr: Dict[str, vtk.vtkImageResliceMapper] = {}
        self.volume_data: Optional[vtk.vtkImageData] = None
        self.opacity_function = vtk.vtkPiecewiseFunction()

        # Caminho dos ícones (ajustado para a estrutura OpenCMF)
        self.path_icones = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "icones"
        )

        self.root_layout = QtWidgets.QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        self._setup_ui()

    def _setup_ui(self):
        # 1. Toolbar de Layout
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setStyleSheet("""
            QToolBar { background: #222; border-bottom: 1px solid #333; spacing: 10px; padding: 4px; }
            QComboBox { background: #333; color: white; border-radius: 2px; min-width: 120px; }
        """)

        self.combo_layout = QtWidgets.QComboBox()
        layouts = [
            ("4 Quadrantes", "4_janelas.png"),
            ("3D Destacado", "3_1.png"),
            ("Apenas 3D", "3D.png")
        ]

        for nome, arquivo in layouts:
            icon_path = os.path.join(self.path_icones, arquivo)
            self.combo_layout.addItem(QtGui.QIcon(icon_path), nome)

        self.combo_layout.currentTextChanged.connect(self.configurar_layout)
        self.toolbar.addWidget(self.combo_layout)
        self.root_layout.addWidget(self.toolbar)

        # 2. Container do Grid
        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(2)
        self.root_layout.addWidget(self.grid_container)

        # 3. Criar vistas 2D
        for nome in self.PLANOS:
            pane = Janela2D(nome)

            # Conexão corrigida: Atualiza o VTK local E emite o sinal para fora
            pane.sliceChanged.connect(lambda v, n=nome: self.update_slice(n, v))
            pane.sliceChanged.connect(lambda v, n=nome: self.sliceChanged.emit(n, v))

            pane.windowLevelChanged.connect(self.update_window_level)
            self.vistas[nome] = pane

        # 4. Criar vista 3D
        pane_3d = Janela3D("3D")
        pane_3d.thresholdChanged.connect(self.update_threshold)
        self.vistas["3D"] = pane_3d

        self.configurar_layout("4 Quadrantes")

    def configurar_layout(self, modo: str):
        # Limpa grid
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i).widget()
            if item: item.setParent(None)

        for p in self.vistas.values(): p.hide()

        if modo == "4 Quadrantes":
            self.grid_layout.addWidget(self.vistas["Axial"], 0, 0)
            self.grid_layout.addWidget(self.vistas["Sagital"], 0, 1)
            self.grid_layout.addWidget(self.vistas["Coronal"], 1, 0)
            self.grid_layout.addWidget(self.vistas["3D"], 1, 1)
        elif modo == "3D Destacado":
            self.grid_layout.addWidget(self.vistas["Axial"], 0, 0)
            self.grid_layout.addWidget(self.vistas["Sagital"], 0, 1)
            self.grid_layout.addWidget(self.vistas["Coronal"], 0, 2)
            self.grid_layout.addWidget(self.vistas["3D"], 1, 0, 1, 3)
        elif modo == "Apenas 3D":
            self.grid_layout.addWidget(self.vistas["3D"], 0, 0)

        for i in range(self.grid_layout.count()):
            self.grid_layout.itemAt(i).widget().show()

    def set_volume(self, volume: vtk.vtkImageData):
        self.volume_data = volume
        extent = volume.GetExtent()

        for nome, pane in self.vistas.items():
            if pane.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer() is None:
                renderer = vtk.vtkRenderer()
                pane.vtkWidget.GetRenderWindow().AddRenderer(renderer)
            else:
                renderer = pane.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()

            if nome == "3D":
                self._configure_3d_renderer(renderer)
            else:
                self._configure_mpr_renderer(renderer, nome)
                axis = self.DIM_MAP[nome]
                total = extent[axis * 2 + 1] - extent[axis * 2] + 1
                pane.slider.blockSignals(True)
                pane.slider.setRange(0, total - 1)
                pane.slider.setValue(total // 2)
                pane.slider.blockSignals(False)

            renderer.ResetCamera()
            pane.vtkWidget.Initialize()
        self.refresh_display()

    def refresh_display(self):
        for pane in self.vistas.values():
            if pane.isVisible():
                pane.vtkWidget.GetRenderWindow().Render()

    def _configure_mpr_renderer(self, renderer, plano: str):
        mapper = vtk.vtkImageResliceMapper()
        mapper.SetInputData(self.volume_data)
        mapper.SliceFacesCameraOn()
        mapper.SliceAtFocalPointOn()
        self.mappers_mpr[plano] = mapper

        # Define a orientação do plano de corte
        plane = vtk.vtkPlane()
        plane.SetNormal(self.NORMALS[plano])
        mapper.SetSlicePlane(plane)

        actor = vtk.vtkImageSlice()
        actor.SetMapper(mapper)
        renderer.AddActor(actor)

        # AJUSTE DA CÂMERA: Força a câmera a olhar para o plano corretamente
        camera = renderer.GetActiveCamera()
        camera.ParallelProjectionOn()

        # Define para onde a câmera olha baseado no plano
        if plano == "Axial":
            camera.SetFocalPoint(0, 0, 0)
            camera.SetPosition(0, 0, 1)  # Olha do topo (Z)
            camera.SetViewUp(0, -1, 0)
        elif plano == "Sagital":
            camera.SetFocalPoint(0, 0, 0)
            camera.SetPosition(1, 0, 0)  # Olha do lado (X)
            camera.SetViewUp(0, 0, 1)
        elif plano == "Coronal":
            camera.SetFocalPoint(0, 0, 0)
            camera.SetPosition(0, 1, 0)  # Olha de frente (Y)
            camera.SetViewUp(0, 0, 1)

    def _configure_3d_renderer(self, renderer):
        mapper = vtk.vtkGPUVolumeRayCastMapper()
        mapper.SetInputData(self.volume_data)
        prop = vtk.vtkVolumeProperty()
        prop.ShadeOn()
        prop.SetScalarOpacity(self.opacity_function)
        vol = vtk.vtkVolume()
        vol.SetMapper(mapper)
        vol.SetProperty(prop)
        renderer.AddActor(vol)
        self.update_threshold(200)

    def update_threshold(self, value: int):
        self.opacity_function.RemoveAllPoints()
        self.opacity_function.AddPoint(value - 100, 0)
        self.opacity_function.AddPoint(value, 1)
        if "3D" in self.vistas:
            self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def update_window_level(self, window: float, level: float):
        self.windowLevelChanged.emit(window, level)

        for nome in self.PLANOS:
            if nome not in self.vistas:
                continue

            pane = self.vistas[nome]
            pane.current_window = window
            pane.current_level = level

            # Acessa o renderer de forma mais direta
            renderer = pane.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
            if not renderer:
                continue

            # Procura especificamente pelo ator da imagem (fatia)
            atores = renderer.GetActors()
            atores.InitTraversal()
            for i in range(atores.GetNumberOfItems()):
                actor = atores.GetNextActor()
                if isinstance(actor, vtk.vtkImageSlice):
                    actor.GetProperty().SetColorWindow(window)
                    actor.GetProperty().SetColorLevel(level)

            # Só renderiza se a aba do Workspace estiver visível
            if pane.isVisible():
                pane.vtkWidget.GetRenderWindow().Render()

    def update_slice(self, plano: str, index: int):
        if plano not in self.mappers_mpr:
            return

        mapper = self.mappers_mpr[plano]
        axis = self.DIM_MAP[plano]

        # 1. Calcula a posição física real baseada na origem e espaçamento do DICOM
        # Formula: Origem + (Indice * Espaçamento)
        pos_fisica = self.volume_data.GetOrigin()[axis] + (index * self.volume_data.GetSpacing()[axis])

        # 2. Atualiza o plano de corte do Mapper
        plane = mapper.GetSlicePlane()
        if plane:
            # Mantém a normal correta para evitar inclinações
            plane.SetNormal(self.NORMALS[plano])

            # Define a nova origem (apenas o eixo correspondente muda)
            origem = list(plane.GetOrigin())
            origem[axis] = pos_fisica
            plane.SetOrigin(origem)

        # 3. Renderiza apenas a janela que mudou (economiza GPU)
        if self.vistas[plano].isVisible():
            self.vistas[plano].vtkWidget.GetRenderWindow().Render()

    def cleanup(self):
        for pane in self.vistas.values():
            if hasattr(pane, 'vtkWidget'):
                pane.vtkWidget.GetRenderWindow().Finalize()