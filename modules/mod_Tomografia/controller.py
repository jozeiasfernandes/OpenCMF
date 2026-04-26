import json
import vtk
from pathlib import Path
from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore
from core.base_module.base import ModuloBase
from core.volume.dicom_engine import DicomEngine
from .ui import TomografiaUI
from core.volume.viewer import VolumeViewerWidget


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

    def _buscar_pasta(self):
        settings = QtCore.QSettings("OpenCMF", "Config")
        ultimo_caminho = settings.value("ultimo_diretorio_dicom", "")

        pasta = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Selecionar Pasta DICOM",
            ultimo_caminho
        )

        if pasta:
            self.ui.edit_dicom.setText(pasta)
            settings.setValue("ultimo_diretorio_dicom", pasta)

    def _validar_dicom(self):
        caminho = self.ui.edit_dicom.text()
        if Path(caminho).exists() and list(Path(caminho).glob("*.dcm")):
            self.caminho_dicom = caminho
            self.ui.update_status_validado()
        else:
            self.ui.update_status_erro()
            QtWidgets.QMessageBox.warning(None, "Erro", "Pasta inválida ou sem arquivos DICOM.")

    def _carregar_dicom(self):
        if not self.caminho_dicom:
            return

        progress = QtWidgets.QProgressDialog("Lendo arquivos DICOM...", "Cancelar", 0, 100, None)
        progress.setWindowTitle("Processando Tomografia")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QtWidgets.QApplication.processEvents()

        try:
            progress.setValue(10)
            sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)

            if sucesso:
                progress.setLabelText("Gerando volume VTI...")
                progress.setValue(40)
                QtWidgets.QApplication.processEvents()

                self._is_initialized = True
                self._persistir_volume()

                progress.setLabelText("Renderizando visualização...")
                progress.setValue(80)

                if self.viewer:
                    self.viewer.set_volume(self.engine.vtk_volume)
                    self.ui.update_status_carregado()

                progress.setValue(100)
                QtWidgets.QMessageBox.information(None, "Sucesso", "Volume processado e salvo com sucesso!")
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
        has_group = hasattr(self.ui, 'group_wl')
        if has_group: self.ui.group_wl.blockSignals(True)
        self.ui.update_wl_ui(window, level)
        if has_group: self.ui.group_wl.blockSignals(False)

    def _wl_manual(self, window: float, level: float):
        if self.viewer:
            self.viewer.update_window_level(window, level)

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.viewer:
            self.viewer.cleanup()
        self.viewer = VolumeViewerWidget()
        self.viewer.sliceChanged.connect(self._sincronizar_fatia)
        self.viewer.windowLevelChanged.connect(self._sincronizar_window_level_ui)
        return self.viewer

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return self.ui.setup_toolboxes(
            on_buscar=self._buscar_pasta,
            on_validar=self._validar_dicom,
            on_carregar=self._carregar_dicom,
            on_wl_manual=self._wl_manual,
            on_finalizar=self._finalizar_etapa
        )