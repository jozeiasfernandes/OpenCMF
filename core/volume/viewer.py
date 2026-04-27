import vtk
import os
import json
from PySide6 import QtWidgets, QtCore, QtGui
from typing import Dict, Optional
from core.windows.window_2d.window_2d import Janela2D
from core.windows.window_3d.window_3d import Janela3D
from core.volume.lookup_table.lut_manager import LUTManager
from core.volume.lookup_table.lut_presets import LUTPresets


class LUTDelegate(QtWidgets.QStyledItemDelegate):
    """Renderiza o degradê de cores diretamente no QComboBox."""

    def paint(self, painter, option, index):
        name = index.data()
        stops = LUTPresets.PRESETS.get(name, [])
        rect = option.rect

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Desenha o fundo de seleção
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(rect, option.palette.highlight())

        # Define o degradê linear baseado nos stops do preset
        gradient = QtGui.QLinearGradient(rect.left() + 5, 0, rect.right() - 5, 0)
        for pos, hex_val in stops:
            gradient.setColorAt(pos, QtGui.QColor(hex_val))

        # Desenha o retângulo do degradê
        grad_rect = rect.adjusted(5, 4, -5, -4)
        painter.setBrush(gradient)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(grad_rect, 3, 3)

        # Desenha o nome do preset centralizado com sombra para legibilidade
        painter.setPen(QtGui.QColor(0, 0, 0, 150))  # Sombra
        painter.drawText(rect.adjusted(1, 1, 1, 1), QtCore.Qt.AlignCenter, name)
        painter.setPen(QtCore.Qt.white)
        painter.drawText(rect, QtCore.Qt.AlignCenter, name)

        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(100, 28)


class VolumeViewerWidget(QtWidgets.QWidget):
    sliceChanged = QtCore.Signal(str, int)
    windowLevelChanged = QtCore.Signal(float, float)

    PLANOS = ["Axial", "Sagital", "Coronal"]
    DIM_MAP = {"Axial": 2, "Sagital": 0, "Coronal": 1}
    NORMALS = {"Axial": (0, 0, 1), "Sagital": (1, 0, 0), "Coronal": (0, 1, 0)}
    VIEW_UP = {"Axial": (0, -1, 0), "Sagital": (0, 0, 1), "Coronal": (0, 0, 1)}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vistas: Dict[str, QtWidgets.QWidget] = {}
        self.mappers_mpr: Dict[str, vtk.vtkImageResliceMapper] = {}
        self.volume_data: Optional[vtk.vtkImageData] = None
        self.opacity_function = vtk.vtkPiecewiseFunction()
        self.color_function = vtk.vtkColorTransferFunction()
        self.volume_actor: Optional[vtk.vtkVolume] = None
        self._init_paths()
        self._setup_main_layout()

    def _init_paths(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.path_presets = os.path.abspath(os.path.join(base_path, "..", "presets"))
        self.path_icones = os.path.abspath(os.path.join(base_path, "..", "..", "icons"))

    def _setup_main_layout(self):
        self.root_layout = QtWidgets.QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        self._setup_toolbar()
        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(2)
        self.root_layout.addWidget(self.grid_container)
        self._create_viewers()
        self.configurar_layout("4 Quadrantes")

    def _setup_toolbar(self):
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setFixedHeight(38)
        self.toolbar.setStyleSheet("""
            QToolBar { background: #1E1E1E; border-bottom: 1px solid #333; spacing: 10px; padding: 0px 8px; } 
            QComboBox { background: #333; color: white; border: 1px solid #444; padding: 2px; min-width: 130px; }
            QLabel { color: #AAA; font-size: 10px; font-weight: bold; }
        """)

        # Layout Combo
        self.toolbar.addWidget(QtWidgets.QLabel("LAYOUT"))
        self.combo_layout = QtWidgets.QComboBox()
        opcoes = [
            ("4 Quadrantes", "4_janelas.png"),
            ("3D Destacado", "3_1.png"),
            ("Apenas 3D", "3D.png"),
            ("Axial", "axial.png"),
            ("Sagital", "sagital.png"),
            ("Coronal", "coronal.png")
        ]
        for nome, img in opcoes:
            path = os.path.join(self.path_icones, img)
            icon = QtGui.QIcon(path) if os.path.exists(path) else QtGui.QIcon()
            self.combo_layout.addItem(icon, nome)

        self.combo_layout.currentTextChanged.connect(self.configurar_layout)
        self.toolbar.addWidget(self.combo_layout)

        self.toolbar.addSeparator()

        # Color Map (LUT) Combo com Degradê
        self.toolbar.addWidget(QtWidgets.QLabel("COLOR MAP"))
        self.combo_lut_global = QtWidgets.QComboBox()
        self.combo_lut_global.setItemDelegate(LUTDelegate(self.combo_lut_global))
        self.combo_lut_global.addItems(list(LUTPresets.PRESETS.keys()))
        self.combo_lut_global.currentTextChanged.connect(self.apply_global_lut)
        self.toolbar.addWidget(self.combo_lut_global)

        self.root_layout.addWidget(self.toolbar)

    def _create_viewers(self):
        cores = {"Axial": "#D32F2F", "Sagital": "#FBC02D", "Coronal": "#388E3C"}
        for nome in self.PLANOS:
            pane = Janela2D(nome, cores[nome])
            pane.sliceChanged.connect(lambda v, n=nome: self.update_slice(n, v))
            pane.maximizeRequested.connect(lambda maximo, n=nome: self._handle_maximize(n, maximo))
            pane.lutChanged.connect(self.apply_global_lut)
            self.vistas[nome] = pane

        pane_3d = Janela3D("3D", "#1976D2")
        pane_3d.thresholdChanged.connect(self.update_threshold)
        pane_3d.viewChanged.connect(self.update_3d_view)
        pane_3d.presetChanged.connect(self.update_preset)
        pane_3d.maximizeRequested.connect(lambda maximo: self._handle_maximize("3D", maximo))
        self.vistas["3D"] = pane_3d

    def apply_global_lut(self, lut_name: str):
        new_lut = LUTManager.get_vtk_lut(lut_name)

        self.combo_lut_global.blockSignals(True)
        self.combo_lut_global.setCurrentText(lut_name)
        self.combo_lut_global.blockSignals(False)

        for nome in self.PLANOS:
            pane = self.vistas.get(nome)
            if pane and hasattr(pane, 'vtk_property') and pane.vtk_property:
                pane.vtk_property.SetLookupTable(new_lut)
                pane.vtkWidget.GetRenderWindow().Render()

    def _handle_maximize(self, nome_vista, is_maximized):
        self.combo_layout.setCurrentText(nome_vista if is_maximized else "4 Quadrantes")

    def set_volume(self, volume: vtk.vtkImageData):
        self.volume_data = volume
        extent = volume.GetExtent()
        centro = volume.GetCenter()
        for nome, pane in self.vistas.items():
            rw = pane.vtkWidget.GetRenderWindow()
            ren = rw.GetRenderers().GetFirstRenderer()
            if not ren:
                ren = vtk.vtkRenderer()
                rw.AddRenderer(ren)
            if nome == "3D":
                self._configure_3d_renderer(ren)
            else:
                self._configure_mpr_renderer(ren, nome)
                axis = self.DIM_MAP[nome]
                min_slice = extent[axis * 2]
                max_slice = extent[axis * 2 + 1]
                pane.slider_corte.setRange(min_slice, max_slice)
                slice_inicial = (min_slice + max_slice) // 2
                pane.slider_corte.setValue(slice_inicial)

                cam = ren.GetActiveCamera()
                cam.SetParallelProjection(True)
                cam.SetFocalPoint(centro)
                pos_cam = list(centro)
                pos_cam[axis] += 1000 if nome != "Axial" else -1000
                cam.SetPosition(pos_cam)
                cam.SetViewUp(self.VIEW_UP[nome])
                self.update_slice(nome, slice_inicial)
                ren.ResetCamera()
            rw.Render()

    def _configure_3d_renderer(self, renderer):
        renderer.RemoveAllViewProps()
        mapper = vtk.vtkSmartVolumeMapper()
        mapper.SetInputData(self.volume_data)
        prop = vtk.vtkVolumeProperty()
        prop.SetColor(self.color_function)
        prop.SetScalarOpacity(self.opacity_function)
        prop.SetInterpolationTypeToLinear()
        self.volume_actor = vtk.vtkVolume()
        self.volume_actor.SetMapper(mapper)
        self.volume_actor.SetProperty(prop)
        renderer.AddActor(self.volume_actor)

        initial_preset = self.vistas["3D"].combo_presets.currentText()
        if initial_preset:
            QtCore.QTimer.singleShot(50, lambda: self.update_preset(initial_preset))
        QtCore.QTimer.singleShot(100, lambda: self.update_3d_view("Frente"))

    def update_preset(self, nome: str):
        if not self.volume_actor: return
        path = os.path.join(self.path_presets, f"{nome}.json")
        if not os.path.exists(path): return
        with open(path, "r") as f:
            preset = json.load(f)

        prop, mapper = self.volume_actor.GetProperty(), self.volume_actor.GetMapper()
        self.color_function.RemoveAllPoints()
        self.opacity_function.RemoveAllPoints()
        for p in preset.get("colors", []): self.color_function.AddRGBPoint(*p)
        for p in preset.get("opacity", []): self.opacity_function.AddPoint(*p)

        threshold = preset.get("threshold", 400)
        self.vistas["3D"].slider_threshold.setValue(threshold)
        self.update_threshold(threshold)

        prop.SetShade(preset.get("shade", True))
        if preset.get("mip", False):
            mapper.SetBlendModeToMaximumIntensity()
        else:
            mapper.SetBlendModeToComposite()

        self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def update_threshold(self, value: int):
        if not self.volume_actor: return
        self.opacity_function.RemoveAllPoints()
        self.opacity_function.AddPoint(value - 100, 0.0)
        self.opacity_function.AddPoint(value, 0.2)
        self.opacity_function.AddPoint(value + 500, 0.8)
        self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def update_3d_view(self, vista: str):
        renderer = self.vistas["3D"].vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        cam = renderer.GetActiveCamera()
        maps = {
            "Frente": (0, -1, 0, 0, 0, 1),
            "Posterior": (0, 1, 0, 0, 0, 1),
            "Superior": (0, 0, 1, 0, -1, 0),
            "Inferior": (0, 0, -1, 0, 1, 0),
            "Direito": (1, 0, 0, 0, 0, 1),
            "Esquerdo": (-1, 0, 0, 0, 0, 1)
        }
        if vista in maps:
            cam.SetPosition(maps[vista][:3])
            cam.SetViewUp(maps[vista][3:])
            cam.SetFocalPoint(0, 0, 0)
            renderer.ResetCamera()
            self.vistas["3D"].vtkWidget.GetRenderWindow().Render()

    def configurar_layout(self, modo: str):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        for v_nome, v_obj in self.vistas.items():
            v_obj.hide()
            if hasattr(v_obj, 'is_maximized'):
                v_obj.is_maximized = (modo == v_nome or (modo == "Apenas 3D" and v_nome == "3D"))
                v_obj._update_maximize_icon()

        mapping = {
            "4 Quadrantes": [("Axial", 0, 0), ("Sagital", 0, 1), ("Coronal", 1, 0), ("3D", 1, 1)],
            "3D Destacado": [("Axial", 0, 0), ("Sagital", 0, 1), ("Coronal", 0, 2), ("3D", 1, 0, 1, 3)],
            "Apenas 3D": [("3D", 0, 0)],
            "Axial": [("Axial", 0, 0)],
            "Sagital": [("Sagital", 0, 0)],
            "Coronal": [("Coronal", 0, 0)]
        }

        for item in mapping.get(modo, []):
            self.grid_layout.addWidget(self.vistas[item[0]], *item[1:])
            self.vistas[item[0]].show()

    def update_slice(self, plano: str, index: int):
        if not self.volume_data or plano not in self.mappers_mpr:
            return

        axis = self.DIM_MAP[plano]
        spacing = self.volume_data.GetSpacing()[axis]
        origin = self.volume_data.GetOrigin()[axis]
        pos_fisica = origin + (index * spacing)

        mapper = self.mappers_mpr[plano]
        plane = mapper.GetSlicePlane()

        novo_origem = list(plane.GetOrigin())
        novo_origem[axis] = pos_fisica
        plane.SetOrigin(novo_origem)

        renderer = self.vistas[plano].vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        camera = renderer.GetActiveCamera()

        focal_point = list(camera.GetFocalPoint())
        camera_pos = list(camera.GetPosition())

        distancia = camera_pos[axis] - focal_point[axis]

        focal_point[axis] = pos_fisica
        camera_pos[axis] = pos_fisica + distancia

        camera.SetFocalPoint(focal_point)
        camera.SetPosition(camera_pos)

        self.vistas[plano].lbl_mm.setText(f"{pos_fisica:.1f} mm")
        self.vistas[plano].vtkWidget.GetRenderWindow().Render()

        self.sliceChanged.emit(plano, index)

    def _configure_mpr_renderer(self, renderer, plano: str):
        renderer.RemoveAllViewProps()

        mapper = vtk.vtkImageResliceMapper()
        mapper.SetInputData(self.volume_data)
        mapper.SliceFacesCameraOff()
        mapper.SliceAtFocalPointOff()

        self.mappers_mpr[plano] = mapper

        plane = vtk.vtkPlane()
        plane.SetNormal(self.NORMALS[plano])
        plane.SetOrigin(self.volume_data.GetCenter())
        mapper.SetSlicePlane(plane)

        vtk_prop = vtk.vtkImageProperty()
        vtk_prop.SetColorWindow(2000)
        vtk_prop.SetColorLevel(400)
        vtk_prop.SetInterpolationTypeToLinear()

        if plano in self.vistas:
            self.vistas[plano].vtk_property = vtk_prop

        actor = vtk.vtkImageSlice()
        actor.SetMapper(mapper)
        actor.SetProperty(vtk_prop)

        renderer.AddActor(actor)

    def refresh_display(self):
        for pane in self.vistas.values():
            if pane.isVisible():
                pane.vtkWidget.GetRenderWindow().Render()