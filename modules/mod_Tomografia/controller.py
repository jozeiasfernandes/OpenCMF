import json
import vtk
from pathlib import Path
from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore
from core.base_module.base import ModuloBase
from core.volume.dicom_engine import DicomEngine
from .ui import TomografiaUI
from core.volume.viewer import VolumeViewerWidget
from .validator import DicomValidator


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Tomografia"
        self.id = "modulo.tomografia"
        self.engine = DicomEngine()
        self.ui = TomografiaUI()
        self.viewer: Optional[VolumeViewerWidget] = None
        self.caminho_dicom: Optional[str] = None
        self._is_initialized = False

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self._carregar_configs_projeto()

    def _carregar_configs_projeto(self):
        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        if not path_info.exists():
            return
        try:
            with open(path_info, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.caminho_dicom = dados.get("caminhos", {}).get("dicom")
                if self.caminho_dicom:
                    self.ui.edit_dicom.setText(self.caminho_dicom)
        except Exception as e:
            print(f"Erro ao carregar info.json: {e}")

    def _atualizar_persistência_diretorio(self, novo_caminho: str):
        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        if not path_info.exists():
            return
        try:
            with open(path_info, "r", encoding="utf-8") as f:
                dados = json.load(f)

            dados.setdefault("caminhos", {})["dicom"] = novo_caminho
            self.caminho_dicom = novo_caminho

            with open(path_info, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao persistir caminho no JSON: {e}")

    def _buscar_pasta(self):
        settings = QtCore.QSettings("OpenCMF", "Config")
        ultimo_caminho = settings.value("ultimo_diretorio_dicom", "")

        pasta = QtWidgets.QFileDialog.getExistingDirectory(
            None, "Selecionar Pasta DICOM ou ZIP", ultimo_caminho
        )

        if pasta:
            self.ui.edit_dicom.setText(pasta)
            settings.setValue("ultimo_diretorio_dicom", pasta)

    def _validar_dicom(self):
        caminho_input = self.ui.edit_dicom.text()
        if not caminho_input:
            return

        progress = QtWidgets.QProgressDialog("Iniciando análise...", "Cancelar", 0, 100, None)
        progress.setWindowTitle("Validador DICOM")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        def update_progress(msg, valor):
            progress.setLabelText(msg)
            progress.setValue(valor)
            QtWidgets.QApplication.processEvents()

        validador = DicomValidator(self.pasta_paciente)
        resultado = validador.analisar_caminho(caminho_input, callback=update_progress)

        progress.close()

        if not resultado["sucesso"]:
            self.ui.update_status_erro()
            QtWidgets.QMessageBox.critical(None, "Erro de Validação", resultado["erro"])
            return

        series = resultado["series"]
        ids_series = list(series.keys())

        if len(ids_series) > 1:
            opcoes = [f"{series[s][0]['desc']} ({len(series[s])} imagens)" for s in ids_series]
            item, ok = QtWidgets.QInputDialog.getItem(
                None, "Múltiplos Estudos",
                "Selecione a série tomográfica correta:", opcoes, 0, False
            )
            if not ok: return
            id_escolhido = ids_series[opcoes.index(item)]
        else:
            id_escolhido = ids_series[0]

        # Pegamos o diretório pai do arquivo para passar para o engine
        caminho_final = str(Path(series[id_escolhido][0]["path"]).parent)
        self._atualizar_persistência_diretorio(caminho_final)
        self.ui.update_status_validado()

        QtWidgets.QMessageBox.information(
            None, "Sucesso",
            f"Série '{series[id_escolhido][0]['desc']}' validada com sucesso."
        )

    def _carregar_dicom(self):
        if not self.caminho_dicom:
            QtWidgets.QMessageBox.warning(None, "Aviso", "Valide a pasta DICOM antes de carregar.")
            return

        progress = QtWidgets.QProgressDialog("Lendo arquivos DICOM...", "Cancelar", 0, 100, None)
        progress.setWindowTitle("Processando Tomografia")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        try:
            progress.setValue(10)
            sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)

            if sucesso:
                progress.setLabelText("Gerando volume binário (VTI)...")
                progress.setValue(40)
                QtWidgets.QApplication.processEvents()

                self._is_initialized = True
                self._persistir_volume()

                progress.setLabelText("Renderizando visualização...")
                progress.setValue(80)

                # Se o viewer já existir na UI, injetamos o volume agora
                if self.viewer:
                    self.viewer.set_volume(self.engine.vtk_volume)
                    self.ui.update_status_carregado()

                progress.setValue(100)
                QtWidgets.QMessageBox.information(None, "Sucesso", "Volume processado com sucesso!")
            else:
                QtWidgets.QMessageBox.critical(None, "Erro", msg)
        finally:
            progress.close()

    def _persistir_volume(self):
        if not self.engine.vtk_volume or not self.pasta_paciente:
            return
        try:
            path_vti = Path(self.pasta_paciente) / "projeto" / "volume.vti"
            writer = vtk.vtkXMLImageDataWriter()
            writer.SetFileName(str(path_vti))
            writer.SetInputData(self.engine.vtk_volume)
            writer.SetCompressorTypeToZLib()
            writer.Write()
        except Exception as e:
            print(f"Erro ao persistir VTI: {e}")

    def _finalizar_etapa(self):
        if not self._is_initialized:
            QtWidgets.QMessageBox.warning(None, "Aviso", "Carregue a tomografia antes de finalizar.")
            return
        self.concluido.emit()

    def _sincronizar_fatia(self, plano: str, valor: int):
        if self.viewer:
            self.viewer.update_slice(plano, valor)

    def _sincronizar_window_level_ui(self, window: float, level: float):
        self.ui.update_wl_ui(window, level)

    def _wl_manual(self, window: float, level: float):
        if self.viewer:
            self.viewer.update_window_level(window, level)

    def get_workspace(self) -> QtWidgets.QWidget:

        if self.viewer:
            self.viewer.cleanup()

        self.viewer = VolumeViewerWidget()
        self.viewer.sliceChanged.connect(self._sincronizar_fatia)
        self.viewer.windowLevelChanged.connect(self._sincronizar_window_level_ui)

        # Se o motor já tiver o volume (ex: carregado via botão), injeta no novo viewer
        if self.engine.vtk_volume:
            self.viewer.set_volume(self.engine.vtk_volume)
            self.ui.update_status_carregado()

        return self.viewer

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return self.ui.setup_toolboxes(
            on_buscar=self._buscar_pasta,
            on_validar=self._validar_dicom,
            on_carregar=self._carregar_dicom,
            on_wl_manual=self._wl_manual,
            on_finalizar=self._finalizar_etapa
        )