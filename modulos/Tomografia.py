import json
import vtk
from pathlib import Path
from typing import Tuple, Optional, Dict
from PySide6 import QtWidgets, QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.base import ModuloBase
from core.dicom_engine import DicomEngine


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Tomografia"
        self.id = "modulo.tomografia"
        self.caminho_dicom: Optional[str] = None
        self._is_initialized = False

        self.engine = DicomEngine()
        self.edit_tomografia = QtWidgets.QLineEdit()
        self.vistas: Dict[str, QVTKRenderWindowInteractor] = {}
        self.mappers_mpr: Dict[str, vtk.vtkImageResliceMapper] = {}

        # Referências de UI
        self.btn_validar = None
        self.btn_carregar = None
        self._main_container = None

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.verificar_pre_requisitos()
        if self.caminho_dicom:
            self.edit_tomografia.setText(self.caminho_dicom)

    def verificar_pre_requisitos(self) -> Tuple[bool, str]:
        if not self.pasta_paciente:
            return False, "Nenhum paciente selecionado."
        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        if not path_info.exists():
            return False, "Arquivo info.json não encontrado."
        try:
            with open(path_info, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.caminho_dicom = dados.get("caminhos", {}).get("dicom")
            return (True, "") if self.caminho_dicom else (False, "Caminho DICOM nulo.")
        except Exception as e:
            return False, str(e)

    # --- LÓGICA DE UI E CARREGAMENTO ---

    def _acao_validar_dicom(self):
        caminho = self.edit_tomografia.text()
        if Path(caminho).exists() and list(Path(caminho).glob("*.dcm")):
            self.caminho_dicom = caminho
            # Feedback visual no botão em vez de MessageBox
            self.btn_validar.setText("✅ DICOM Validado")
            self.btn_validar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
            if self.btn_carregar:
                self.btn_carregar.setEnabled(True)
        else:
            self.btn_validar.setText("❌ Erro na Pasta")
            QtWidgets.QMessageBox.warning(None, "Erro", "Pasta inválida ou sem arquivos .dcm")

    def _acao_carregar_dicom(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)
            if sucesso:
                self._configurar_visualizadores_vtk()
                self._is_initialized = True

                QtWidgets.QApplication.processEvents()
                bounds = self.engine.vtk_volume.GetBounds()
                max_dim = max(bounds[1] - bounds[0], bounds[3] - bounds[2])

                for nome, widget in self.vistas.items():
                    ren = widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
                    if ren and nome != "3D":
                        cam = ren.GetActiveCamera()
                        cam.SetParallelScale(max_dim / 2.0)
                        ren.ResetCamera()
                        widget.GetRenderWindow().Render()

                # Feedback visual de conclusão
                self.btn_carregar.setText("✅ DICOM concluído")
                self.btn_carregar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    # --- INTERFACE ---

    def get_workspace(self) -> QtWidgets.QWidget:
        if self._main_container:
            self._main_container.deleteLater()

        self.vistas.clear()
        self.mappers_mpr.clear()

        self._main_container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self._main_container)
        layout.setContentsMargins(0, 0, 0, 0)

        view_area = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(view_area)
        grid.setSpacing(2)

        planos = ["Axial", "Sagital", "Coronal", "3D"]
        for i, nome in enumerate(planos):
            vtkWidget = QVTKRenderWindowInteractor(view_area)
            vtkWidget.setStyleSheet("border: 1px solid #333; background-color: black;")

            lbl = QtWidgets.QLabel(nome, vtkWidget)
            lbl.setStyleSheet("color: #3ea6fa; background: rgba(0, 0, 0, 150); font-weight: bold; padding: 2px;")
            lbl.move(10, 10)
            lbl.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

            if nome != "3D":
                vtkWidget.AddObserver("MouseWheelForwardEvent", self._on_scroll_up)
                vtkWidget.AddObserver("MouseWheelBackwardEvent", self._on_scroll_down)

            self.vistas[nome] = vtkWidget
            grid.addWidget(vtkWidget, i // 2, i % 2)

        layout.addWidget(view_area, stretch=1)
        return self._main_container

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        aba_abrir = QtWidgets.QWidget()
        lay_abrir = QtWidgets.QVBoxLayout(aba_abrir)
        lay_abrir.addWidget(QtWidgets.QLabel("<b>GESTÃO DE ARQUIVOS</b>"))

        form = QtWidgets.QFormLayout()

        def criar_linha(edit, callback):
            w = QtWidgets.QWidget()
            l = QtWidgets.QHBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            l.addWidget(edit)
            b = QtWidgets.QPushButton("...")
            b.setFixedWidth(30)
            b.clicked.connect(lambda: callback(edit, True))
            l.addWidget(b)
            return w

        form.addRow("Tomografia:", criar_linha(self.edit_tomografia, self._buscar_caminho))
        lay_abrir.addLayout(form)

        self.btn_validar = QtWidgets.QPushButton("🔍 Validar DICOM")
        self.btn_validar.clicked.connect(self._acao_validar_dicom)
        lay_abrir.addWidget(self.btn_validar)

        self.btn_carregar = QtWidgets.QPushButton("⌛​ Carregar DICOM")
        self.btn_carregar.setEnabled(False)
        self.btn_carregar.setStyleSheet("font-weight: bold; background-color: #2980b9; color: white;")
        self.btn_carregar.clicked.connect(self._acao_carregar_dicom)
        lay_abrir.addWidget(self.btn_carregar)

        lay_abrir.addStretch()
        btn_c = QtWidgets.QPushButton("Finalizar Etapa")
        btn_c.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_c.clicked.connect(self._on_conclude_clicked)
        lay_abrir.addWidget(btn_c)

        aba_filtrar = QtWidgets.QWidget()
        lay_f = QtWidgets.QVBoxLayout(aba_filtrar)
        lay_f.addWidget(QtWidgets.QLabel("<b>FILTROS DICOM</b>"))
        self.slider_hu = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_hu.setRange(-1000, 3000)
        self.slider_hu.setValue(200)
        self.slider_hu.valueChanged.connect(self._atualizar_threshold_3d)
        lay_f.addWidget(QtWidgets.QLabel("Threshold (HU):"))
        lay_f.addWidget(self.slider_hu)
        lay_f.addStretch()

        return {"Abrir": aba_abrir, "Filtrar": aba_filtrar}

    def _buscar_caminho(self, edit, is_dir):
        p = QtWidgets.QFileDialog.getExistingDirectory(None, "Pasta DICOM")
        if p:
            edit.setText(p)
            self.btn_validar.setText("🔍 Validar DICOM")
            self.btn_validar.setStyleSheet("")

    def _configurar_visualizadores_vtk(self):
        if not self.engine.vtk_volume: return
        for nome, widget in self.vistas.items():
            ren = vtk.vtkRenderer()
            widget.GetRenderWindow().AddRenderer(ren)
            if nome == "3D":
                self._setup_3d_view(ren)
            else:
                self._setup_mpr_view(ren, nome)
            ren.ResetCamera()
            widget.Initialize()

    def _setup_mpr_view(self, renderer, plano):
        reslice_mapper = vtk.vtkImageResliceMapper()
        reslice_mapper.SetInputData(self.engine.vtk_volume)
        reslice_mapper.SliceFacesCameraOn()
        reslice_mapper.SliceAtFocalPointOn()
        reslice_mapper.SetResampleToScreenPixels(True)

        self.mappers_mpr[plano] = reslice_mapper
        corte_plano = vtk.vtkPlane()

        # Definição rigorosa das normais para evitar confusão entre Sagital e Coronal
        normais = {
            "Axial": (0, 0, 1),
            "Sagital": (1, 0, 0),
            "Coronal": (0, 1, 0)
        }

        corte_plano.SetNormal(normais.get(plano, (0, 0, 1)))
        reslice_mapper.SetSlicePlane(corte_plano)

        slice_actor = vtk.vtkImageSlice()
        slice_actor.SetMapper(reslice_mapper)
        renderer.AddActor(slice_actor)
        renderer.SetBackground(0.05, 0.05, 0.05)

        volume_bounds = self.engine.vtk_volume.GetBounds()
        centro = [(volume_bounds[i * 2] + volume_bounds[i * 2 + 1]) / 2.0 for i in range(3)]

        camera = renderer.GetActiveCamera()
        camera.ParallelProjectionOn()
        camera.SetFocalPoint(centro)

        if plano == "Axial":
            camera.SetPosition(centro[0], centro[1], centro[2] + 1000)
            camera.SetViewUp(0, -1, 0)
        elif plano == "Sagital":
            camera.SetPosition(centro[0] + 1000, centro[1], centro[2])
            camera.SetViewUp(0, 0, 1)
        elif plano == "Coronal":
            camera.SetPosition(centro[0], centro[1] - 1000, centro[2])
            camera.SetViewUp(0, 0, 1)

    def _setup_3d_view(self, renderer):
        mapper = vtk.vtkGPUVolumeRayCastMapper()
        mapper.SetInputData(self.engine.vtk_volume)
        prop = vtk.vtkVolumeProperty()
        prop.ShadeOn()
        prop.SetInterpolationTypeToLinear()
        opac = vtk.vtkPiecewiseFunction()
        opac.AddPoint(100, 0)
        opac.AddPoint(200, 1)
        prop.SetScalarOpacity(opac)
        vol = vtk.vtkVolume()
        vol.SetMapper(mapper)
        vol.SetProperty(prop)
        renderer.AddActor(vol)
        renderer.SetBackground(0.1, 0.1, 0.15)

    def _on_scroll_up(self, obj, ev):
        self._navegar_fatia(obj, 1)

    def _on_scroll_down(self, obj, ev):
        self._navegar_fatia(obj, -1)

    def _navegar_fatia(self, interactor, delta):
        n = next((k for k, v in self.vistas.items() if v == interactor), None)
        m = self.mappers_mpr.get(n)
        if m:
            idx = m.GetSliceIndex()
            novo = idx + delta
            if 0 <= novo < m.GetTotalSlices():
                m.SetSliceIndex(novo)
                interactor.GetRenderWindow().Render()

    def _atualizar_threshold_3d(self, v):
        if "3D" in self.vistas:
            ren = self.vistas["3D"].GetRenderWindow().GetRenderers().GetFirstRenderer()
            vol = ren.GetVolumes().GetLastProp()
            if vol:
                o = vtk.vtkPiecewiseFunction()
                o.AddPoint(v - 100, 0)
                o.AddPoint(v, 1)
                vol.GetProperty().SetScalarOpacity(o)
                self.vistas["3D"].GetRenderWindow().Render()

    def _on_conclude_clicked(self):
        if self._is_initialized:
            self.concluido.emit()
        else:
            QtWidgets.QMessageBox.warning(None, "Erro", "Módulo não inicializado.")