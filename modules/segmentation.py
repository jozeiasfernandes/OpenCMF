import os
import json
import vtk
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from core.base_module.base import ModuloBase
from core.volume.viewer import VolumeViewerWidget
from core.volume.segmentation_engine import SegmentacaoEngine
from core.toolboxes.object_manager_widget import ObjetoManagerWidget
from core.toolboxes.segmentation_widget import SegmentacaoWidget


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Segmentação"
        self.id = "modulo.segmentacao"
        self.viewer: Optional[VolumeViewerWidget] = None
        self.engine_seg = SegmentacaoEngine()
        self.volume_data = None
        self.widget_seg = SegmentacaoWidget()
        self.widget_objetos = ObjetoManagerWidget()
        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_seg.pathChanged.connect(self._on_path_changed)
        self.widget_seg.thresholdChanged.connect(self._on_hu_changed)
        self.widget_seg.solicitarMascara.connect(self._executar_threshold)
        self.widget_seg.solicitarExportarSTL.connect(self._executar_exportacao_stl)
        self.widget_objetos.objetoToggled.connect(self._on_objeto_toggled)
        self.widget_objetos.requestRefresh.connect(self._atualizar_lista_objetos)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        path_json = Path(caminho_paciente) / "projeto" / "info.json"
        if path_json.exists():
            try:
                with open(path_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                caminho_dicom = data.get("caminhos", {}).get("dicom", "")
                self.widget_seg.set_path(caminho_dicom)
                self._carregar_volume_otimizado(caminho_dicom)
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
        self._atualizar_lista_objetos()

    def _on_path_changed(self, novo_caminho):
        if os.path.exists(novo_caminho) and os.path.isdir(novo_caminho):
            self._carregar_volume_otimizado(novo_caminho)

    def _carregar_volume_otimizado(self, caminho_dicom: str):
        """Prioriza carregar o arquivo VTI compactado para economizar RAM."""
        path_vti = Path(self.pasta_paciente) / "projeto" / "volume.vti"
        try:
            if path_vti.exists():
                reader = vtk.vtkXMLImageDataReader()
                reader.SetFileName(str(path_vti))
                reader.Update()
                self.volume_data = reader.GetOutput()
            elif caminho_dicom and os.path.exists(caminho_dicom):
                from core.volume.dicom_engine import DicomEngine
                self.volume_data = DicomEngine().carregar_volume(caminho_dicom)

            if self.viewer and self.volume_data:
                self.viewer.set_volume(self.volume_data)
        except Exception as e:
            print(f"Falha na carga do volume: {e}")

    def _on_hu_changed(self, val):
        if self.viewer and hasattr(self.viewer, 'update_threshold'):
            self.viewer.update_threshold(val)

    def _executar_threshold(self):
        if not self.volume_data:
            return QtWidgets.QMessageBox.warning(None, "Aviso", "Volume não carregado.")
        hu_min = self.widget_seg.get_value()
        if self.engine_seg.gerar_mascara(self.volume_data, hu_min):
            QtWidgets.QMessageBox.information(None, "Sucesso", "Máscara gerada.")

    def _executar_exportacao_stl(self):
        if not self.engine_seg.mask_data:
            return QtWidgets.QMessageBox.warning(None, "Aviso", "Gere a máscara primeiro.")

        qualidade_idx = self.widget_seg.get_qualidade_index()
        progress = QtWidgets.QProgressDialog("Processando...", None, 0, 5, self.widget_seg)
        progress.setWindowModality(QtCore.Qt.WindowModal)

        dir_stl = Path(self.pasta_paciente) / "STL"
        dir_stl.mkdir(parents=True, exist_ok=True)
        caminho_saida = dir_stl / "osso_segmentado.stl"

        def callback(msg, val):
            progress.setLabelText(msg);
            progress.setValue(val)
            QtWidgets.QApplication.processEvents()

        if self.engine_seg.exportar_stl(self.engine_seg.mask_data, caminho_saida, qualidade_idx, callback):
            self._atualizar_lista_objetos()
            QtWidgets.QMessageBox.information(None, "Sucesso", "Malha exportada.")
        progress.close()

    def _atualizar_lista_objetos(self):
        if self.widget_objetos and self.pasta_paciente:
            self.widget_objetos.atualizar_lista(pasta_stl=str(Path(self.pasta_paciente) / "STL"))

    def _on_objeto_toggled(self, nome, visivel):
        if not self.viewer: return
        if nome == "volume DICOM":
            self.viewer.set_visibilidade_objeto(nome, visivel)
        else:
            self._gerenciar_visualizacao_stl(nome, visivel)

    def _gerenciar_visualizacao_stl(self, nome, visivel):
        if visivel and nome not in self.viewer.objetos_3d:
            path = Path(self.pasta_paciente) / "STL" / nome
            if path.exists():
                reader = vtk.vtkSTLReader()
                reader.SetFileName(str(path))
                reader.Update()
                self.viewer.adicionar_malha_3d(nome, reader.GetOutput())
        self.viewer.set_visibilidade_objeto(nome, visivel)

    def get_workspace(self) -> QtWidgets.QWidget:
        if not self.viewer:
            self.viewer = VolumeViewerWidget()
            self.viewer.configurar_layout("Apenas 3D")
            if self.volume_data: self.viewer.set_volume(self.volume_data)
        return self.viewer

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {"Segmentação": self.widget_seg, "Objetos": self.widget_objetos}