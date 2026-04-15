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
        self.list_objetos: Optional[QtWidgets.QListWidget] = None

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
        self._atualizar_lista_objetos()

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
        # --- ABA SEGMENTAÇÃO ---
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

        # --- ABA OBJETOS ---
        aba_obj = QtWidgets.QWidget()
        lay_obj = QtWidgets.QVBoxLayout(aba_obj)

        self.list_objetos = QtWidgets.QListWidget()
        self.list_objetos.setAlternatingRowColors(True)

        btn_refresh = QtWidgets.QPushButton(" Atualizar Lista")
        btn_refresh.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))
        btn_refresh.clicked.connect(self._atualizar_lista_objetos)

        lay_obj.addWidget(QtWidgets.QLabel("Arquivos STL na pasta:"))
        lay_obj.addWidget(self.list_objetos)
        lay_obj.addWidget(btn_refresh)

        if self.pasta_paciente:
            self._atualizar_lista_objetos()

        return {"Segmentação": aba_seg, "Objetos": aba_obj}

    def _atualizar_lista_objetos(self):
        if not self.list_objetos or not self.pasta_paciente:
            return

        self.list_objetos.blockSignals(True)  # Evita disparar eventos enquanto popula
        self.list_objetos.clear()

        # Adiciona o "Volume DICOM" como primeiro item fixo
        item_vol = QtWidgets.QListWidgetItem("Volume DICOM (Original)")
        item_vol.setFlags(item_vol.flags() | QtCore.Qt.ItemIsUserCheckable)
        item_vol.setCheckState(QtCore.Qt.Checked)
        self.list_objetos.addItem(item_vol)

        diretorio_stl = Path(self.pasta_paciente) / "STL"
        if diretorio_stl.exists():
            for arquivo in diretorio_stl.glob("*.stl"):
                item = QtWidgets.QListWidgetItem(arquivo.name)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)  # Começa oculto
                item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
                self.list_objetos.addItem(item)

        self.list_objetos.blockSignals(False)

    def _buscar_caminho(self, target, folder=True):
        p = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecionar Pasta DICOM")
        if p: target.setText(p)

    def _on_hu_changed(self, val):
        self.lbl_hu_value.setText(f"Mínimo: {val} HU")
        if self.viewer and hasattr(self.viewer, 'update_threshold'):
            self.viewer.update_threshold(val)

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
            QtWidgets.QMessageBox.information(None, "Sucesso", f"Malha salva com sucesso!")

        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(None, "Erro", f"Falha ao exportar STL: {e}")

    def _on_objeto_toggled(self, item):
        visivel = (item.checkState() == QtCore.Qt.Checked)
        nome = item.text()

        if nome == "Volume DICOM (Original)":
            # Comando para o viewer ocultar o volume principal
            if self.viewer:
                self.viewer.set_volume_visibility(visivel)
        else:
            # Carregar o STL e enviar para o viewer se for a primeira vez,
            # ou apenas alternar visibilidade
            self._gerenciar_visualizacao_stl(nome, visivel)

    def _gerenciar_visualizacao_stl(self, nome_arquivo, visivel):
        caminho = Path(self.pasta_paciente) / "STL" / nome_arquivo

        # Se estiver ligando e o objeto ainda não existe no viewer, carregamos
        if visivel and nome_arquivo not in self.viewer.objetos_3d:
            reader = vtk.vtkSTLReader()
            reader.SetFileName(str(caminho))
            reader.Update()
            self.viewer.adicionar_malha(nome_arquivo, reader.GetOutput())

        # Alterna a visibilidade no viewer
        self.viewer.alternar_visibilidade(nome_arquivo, visivel)