import vtk
import os
import json
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from core.modulo_base.base import ModuloBase
from core.volume.viewer import VolumeViewerWidget
from core.widgets.objeto_manager_widget import ObjetoManagerWidget
from modulos.mod_Paciente.ui_components import criar_linha_arquivo

class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Segmentação"
        self.id = "modulo.segmentacao"
        self.pasta_paciente = None

        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_tomografia.textChanged.connect(self._on_path_changed)

        self._is_initialized = False
        self.viewer: Optional[VolumeViewerWidget] = None
        self.volume_data: Optional[vtk.vtkImageData] = None
        self.mask_data: Optional[vtk.vtkImageData] = None
        self.widget_objetos: Optional[ObjetoManagerWidget] = None

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.pasta_paciente = caminho_paciente
        path_json = Path(caminho_paciente) / "projeto" / "info.json"

        if path_json.exists():
            try:
                with open(path_json, "r", encoding="utf-8") as f:
                    data = json.load(f)

                caminho_dicom = data.get("caminhos", {}).get("dicom", "")

                self.edit_tomografia.blockSignals(True)
                self.edit_tomografia.setText(caminho_dicom)
                self.edit_tomografia.blockSignals(False)

                if caminho_dicom and os.path.exists(caminho_dicom):
                    self._carregar_dicom(caminho_dicom)
            except Exception as e:
                print(f"Erro ao carregar info do paciente: {e}")

        self._is_initialized = True
        self._atualizar_lista_objetos()

    def _buscar_caminho(self, target, folder=True):
        p = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecionar Pasta DICOM")
        if p: target.setText(p)

    def _on_path_changed(self, novo_caminho):
        if os.path.exists(novo_caminho) and os.path.isdir(novo_caminho):
            self._carregar_dicom(novo_caminho)

    def _on_hu_changed(self, val):
        self.lbl_hu_value.setText(f"Mínimo: {val} HU")
        if self.viewer and hasattr(self.viewer, 'update_threshold'):
            self.viewer.update_threshold(val)

    def _carregar_dicom(self, caminho: str):
        try:
            from core.volume.dicom_engine import DicomEngine
            engine = DicomEngine()
            self.volume_data = engine.carregar_volume(caminho)

            if self.viewer and self.volume_data:
                self.viewer.set_volume(self.volume_data)
        except Exception as e:
            print(f"Erro no carregamento DICOM: {e}")

    def _run_threshold(self):
        if not self.volume_data: return
        thresh = vtk.vtkImageThreshold()
        thresh.SetInputData(self.volume_data)
        thresh.ThresholdByUpper(self.slider_hu.value())
        thresh.SetInValue(1)
        thresh.SetOutValue(0)
        thresh.Update()
        self.mask_data = thresh.GetOutput()
        QtWidgets.QMessageBox.information(None, "Sucesso", "Máscara gerada.")

    def _gerar_STL(self):
        if not self.mask_data:
            QtWidgets.QMessageBox.warning(None, "Aviso", "Gere a máscara antes de exportar!")
            return

        diretorio_stl = Path(self.pasta_paciente) / "STL"
        try:
            diretorio_stl.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Erro", f"Erro de pasta: {e}")
            return

        caminho_saida = diretorio_stl / "osso_segmentado.stl"
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        try:
            mesh_filter = vtk.vtkFlyingEdges3D()
            mesh_filter.SetInputData(self.mask_data)
            mesh_filter.SetValue(0, 0.5)
            mesh_filter.Update()

            connectivity = vtk.vtkPolyDataConnectivityFilter()
            connectivity.SetInputConnection(mesh_filter.GetOutputPort())
            connectivity.SetExtractionModeToLargestRegion()
            connectivity.Update()

            decimator = vtk.vtkDecimatePro()
            decimator.SetInputConnection(connectivity.GetOutputPort())
            decimator.SetTargetReduction(0.85)
            decimator.PreserveTopologyOn()
            decimator.Update()

            smoother = vtk.vtkWindowedSincPolyDataFilter()
            smoother.SetInputConnection(decimator.GetOutputPort())
            smoother.SetNumberOfIterations(40)
            smoother.SetPassBand(0.01)
            smoother.BoundarySmoothingOff()
            smoother.NonManifoldSmoothingOn()
            smoother.NormalizeCoordinatesOn()
            smoother.Update()

            writer = vtk.vtkSTLWriter()
            writer.SetFileName(str(caminho_saida))
            writer.SetInputData(smoother.GetOutput())
            writer.SetFileTypeToBinary()
            writer.Write()

            self._atualizar_lista_objetos()
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.information(None, "Sucesso", f"Malha salva e adicionada à lista!")

        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(None, "Erro", f"Falha ao exportar STL: {e}")

    def _atualizar_lista_objetos(self):
        if self.widget_objetos and self.pasta_paciente:
            pasta_stl = str(Path(self.pasta_paciente) / "STL")
            self.widget_objetos.atualizar_lista(pasta_stl=pasta_stl)

    def _on_objeto_toggled(self, nome, visivel):
        if not self.viewer: return

        if nome == "volume DICOM":
            self.viewer.set_visibilidade_objeto(nome, visivel)
        else:
            self._gerenciar_visualizacao_stl(nome, visivel)

    def _gerenciar_visualizacao_stl(self, nome_arquivo, visivel):
        if visivel and nome_arquivo not in self.viewer.objetos_3d:
            caminho = Path(self.pasta_paciente) / "STL" / nome_arquivo
            if caminho.exists():
                reader = vtk.vtkSTLReader()
                reader.SetFileName(str(caminho))
                reader.Update()
                self.viewer.adicionar_malha_3d(nome_arquivo, reader.GetOutput())

        self.viewer.set_visibilidade_objeto(nome_arquivo, visivel)

    def get_workspace(self) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.viewer = VolumeViewerWidget()
        self.viewer.configurar_layout("Apenas 3D")
        if self.volume_data:
            self.viewer.set_volume(self.volume_data)

        layout.addWidget(self.viewer, stretch=1)
        return container

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        # Aba Segmentação
        aba_seg = QtWidgets.QWidget()
        lay_seg = QtWidgets.QVBoxLayout(aba_seg)
        lay_seg.setSpacing(10)

        group_arq = QtWidgets.QGroupBox("Fonte de Dados")
        lay_arq = QtWidgets.QVBoxLayout(group_arq)
        lay_arq.addWidget(criar_linha_arquivo(self.edit_tomografia, self._buscar_caminho, True))
        lay_seg.addWidget(group_arq)

        group_thresh = QtWidgets.QGroupBox("Filtro de Densidade (HU)")
        lay_thresh = QtWidgets.QVBoxLayout(group_thresh)
        self.slider_hu = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_hu.setRange(-1000, 3000)
        self.slider_hu.setValue(226)
        self.slider_hu.valueChanged.connect(self._on_hu_changed)
        self.lbl_hu_value = QtWidgets.QLabel("Mínimo: 226 HU")
        self.lbl_hu_value.setAlignment(QtCore.Qt.AlignCenter)
        lay_thresh.addWidget(self.lbl_hu_value)
        lay_thresh.addWidget(self.slider_hu)
        lay_seg.addWidget(group_thresh)

        btn_preview = QtWidgets.QPushButton(" Gerar Máscara")
        btn_preview.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        btn_preview.clicked.connect(self._run_threshold)
        lay_seg.addWidget(btn_preview)
        lay_seg.addStretch()

        btn_stl = QtWidgets.QPushButton(" Exportar STL")
        btn_stl.setStyleSheet("background-color: #2d5a27; color: white; font-weight: bold; padding: 10px;")
        btn_stl.clicked.connect(self._gerar_STL)
        lay_seg.addWidget(btn_stl)

        # Aba Objetos (Gerenciada pelo Core)
        self.widget_objetos = ObjetoManagerWidget()
        self.widget_objetos.objetoToggled.connect(self._on_objeto_toggled)
        self.widget_objetos.requestRefresh.connect(self._atualizar_lista_objetos)

        if self.pasta_paciente:
            self._atualizar_lista_objetos()

        for aba in [aba_seg, self.widget_objetos]:
            aba.setMinimumWidth(320)
            aba.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        return {"Segmentação": aba_seg, "Objetos": self.widget_objetos}