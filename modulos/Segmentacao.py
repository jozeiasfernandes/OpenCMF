import vtk
import os
import json
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from core.base import ModuloBase
from modulos.mod_Tomografia.viewers import VolumeViewerWidget
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
                    self._carregar_volume_dicom(caminho_dicom)
            except Exception as e:
                print(f"Erro ao carregar info do paciente: {e}")

        self._is_initialized = True

    def _carregar_volume_dicom(self, caminho: str):
        try:
            from core.dicom_engine import DicomEngine
            engine = DicomEngine()
            self.volume_data = engine.carregar_volume(caminho)

            if self.viewer and self.volume_data:
                self.viewer.set_volume(self.volume_data)
        except Exception as e:
            print(f"Erro no carregamento DICOM: {e}")

    def _on_path_changed(self, novo_caminho):
        if os.path.exists(novo_caminho) and os.path.isdir(novo_caminho):
            self._carregar_volume_dicom(novo_caminho)

    def get_workspace(self) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.viewer = VolumeViewerWidget()
        if self.volume_data:
            self.viewer.set_volume(self.volume_data)

        layout.addWidget(self.viewer, stretch=1)
        return container

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        aba = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(aba)
        layout.setSpacing(10)

        group_arq = QtWidgets.QGroupBox("Fonte de Dados")
        lay_arq = QtWidgets.QVBoxLayout(group_arq)
        linha_arq = criar_linha_arquivo(self.edit_tomografia, self._buscar_caminho, True)
        lay_arq.addWidget(linha_arq)
        layout.addWidget(group_arq)

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
        layout.addWidget(group_thresh)

        btn_preview = QtWidgets.QPushButton(" Gerar Máscara")
        btn_preview.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        btn_preview.clicked.connect(self._run_threshold)
        layout.addWidget(btn_preview)

        layout.addStretch()

        btn_stl = QtWidgets.QPushButton(" Exportar STL")
        btn_stl.setStyleSheet("background-color: #2d5a27; color: white; font-weight: bold; padding: 10px;")
        btn_stl.clicked.connect(self._gerar_STL)
        layout.addWidget(btn_stl)

        return {"Segmentação": aba}

    def _buscar_caminho(self, target, folder=True):
        p = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecionar Pasta DICOM")
        if p: target.setText(p)

    def _on_hu_changed(self, val):
        self.lbl_hu_value.setText(f"Mínimo: {val} HU")
        if self.viewer and hasattr(self.viewer, 'update_threshold'):
            self.viewer.update_threshold(val)

    def _run_threshold(self):
        if not self.volume_data:
            return

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
            # 1. Extração inicial
            mesh_filter = vtk.vtkFlyingEdges3D()
            mesh_filter.SetInputData(self.mask_data)
            mesh_filter.SetValue(0, 0.5)
            mesh_filter.Update()

            # 2. LIMPEZA: Remove polígonos isolados (ruído flutuante)
            # Mantém apenas a maior estrutura (geralmente o crânio/mandíbula)
            connectivity = vtk.vtkPolyDataConnectivityFilter()
            connectivity.SetInputConnection(mesh_filter.GetOutputPort())
            connectivity.SetExtractionModeToLargestRegion()
            connectivity.Update()

            # 3. DECIMAÇÃO MODERADA: Redução equilibrada (85%)
            decimator = vtk.vtkDecimatePro()
            decimator.SetInputConnection(connectivity.GetOutputPort())
            decimator.SetTargetReduction(0.85)
            decimator.PreserveTopologyOn()
            decimator.Update()

            # 4. SMOOTH AGRESSIVO: Suavização Windowed Sinc (preserva volume melhor que Laplacian)
            smoother = vtk.vtkWindowedSincPolyDataFilter()
            smoother.SetInputConnection(decimator.GetOutputPort())
            smoother.SetNumberOfIterations(40)  # Mais iterações para polir a superfície
            smoother.SetPassBand(0.01)          # Quanto menor, mais suave/arredondado
            smoother.BoundarySmoothingOff()
            smoother.NonManifoldSmoothingOn()
            smoother.NormalizeCoordinatesOn()
            smoother.Update()

            # 5. SALVAMENTO BINÁRIO
            writer = vtk.vtkSTLWriter()
            writer.SetFileName(str(caminho_saida))
            writer.SetInputData(smoother.GetOutput())
            writer.SetFileTypeToBinary()
            writer.Write()

            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.information(None, "Sucesso", f"Malha limpa e suavizada salva em:\n{caminho_saida}")

        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(None, "Erro", f"Falha ao exportar STL: {e}")