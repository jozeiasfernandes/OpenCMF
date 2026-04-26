import os
import json
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

        # Motores e Visualização
        self.viewer: Optional[VolumeViewerWidget] = None
        self.engine_seg = SegmentacaoEngine()
        self.volume_data = None  # Armazena o vtkImageData original

        # Widgets de Interface (Core)
        self.widget_seg = SegmentacaoWidget()
        self.widget_objetos = ObjetoManagerWidget()

        self._conectar_sinais()

    def _conectar_sinais(self):
        # Sinais do Widget de Segmentação
        self.widget_seg.pathChanged.connect(self._on_path_changed)
        self.widget_seg.thresholdChanged.connect(self._on_hu_changed)
        self.widget_seg.solicitarMascara.connect(self._executar_threshold)
        self.widget_seg.solicitarExportarSTL.connect(self._executar_exportacao_stl)

        # Sinais do Gerenciador de Objetos
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
                if caminho_dicom and os.path.exists(caminho_dicom):
                    self._carregar_dicom(caminho_dicom)
            except Exception as e:
                print(f"Erro ao carregar dados do projeto: {e}")

        self._atualizar_lista_objetos()

    def _on_path_changed(self, novo_caminho):
        if os.path.exists(novo_caminho) and os.path.isdir(novo_caminho):
            self._carregar_dicom(novo_caminho)

    def _on_hu_changed(self, val):
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

    def _executar_threshold(self):
        if not self.volume_data:
            QtWidgets.QMessageBox.warning(None, "Aviso", "Carregue um volume DICOM primeiro.")
            return

        hu_min = self.widget_seg.get_value()
        mask = self.engine_seg.gerar_mascara(self.volume_data, hu_min)

        if mask:
            QtWidgets.QMessageBox.information(None, "Sucesso", "Máscara de segmentação gerada.")

    def _executar_exportacao_stl(self):
        if not self.engine_seg.mask_data:
            QtWidgets.QMessageBox.warning(None, "Aviso", "Gere a máscara antes de exportar!")
            return

        # Captura a qualidade selecionada no widget (Alta=0, Média=1, Baixa=2)
        qualidade_idx = self.widget_seg.get_qualidade_index()

        # Configuração da Janela de Progresso
        progress = QtWidgets.QProgressDialog("Iniciando...", None, 0, 5, self.widget_seg)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setWindowTitle("Processando Malha 3D")
        progress.setMinimumDuration(0)
        progress.setValue(0)
        QtWidgets.QApplication.processEvents()

        # Definição do destino
        diretorio_stl = Path(self.pasta_paciente) / "STL"
        diretorio_stl.mkdir(parents=True, exist_ok=True)
        caminho_saida = diretorio_stl / "osso_segmentado.stl"

        def callback_progresso(msg, valor):
            progress.setLabelText(msg)
            progress.setValue(valor)
            QtWidgets.QApplication.processEvents()

        # Chama o processamento passando a qualidade selecionada
        sucesso = self.engine_seg.exportar_stl(
            self.engine_seg.mask_data,
            caminho_saida,
            qualidade_idx,
            callback_progresso
        )

        progress.close()

        if sucesso:
            self._atualizar_lista_objetos()
            QtWidgets.QMessageBox.information(None, "Sucesso", f"Malha exportada com sucesso:\n{caminho_saida.name}")
        else:
            QtWidgets.QMessageBox.critical(None, "Erro", "Falha crítica na geração do arquivo STL.")

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
            import vtk
            caminho = Path(self.pasta_paciente) / "STL" / nome_arquivo
            if caminho.exists():
                reader = vtk.vtkSTLReader()
                reader.SetFileName(str(caminho))
                reader.Update()
                self.viewer.adicionar_malha_3d(nome_arquivo, reader.GetOutput())
        self.viewer.set_visibilidade_objeto(nome_arquivo, visivel)

    def get_workspace(self) -> QtWidgets.QWidget:
        if not self.viewer:
            self.viewer = VolumeViewerWidget()
            self.viewer.configurar_layout("Apenas 3D")
            if self.volume_data:
                self.viewer.set_volume(self.volume_data)
        return self.viewer

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Segmentação": self.widget_seg,
            "Objetos": self.widget_objetos
        }