import json
from pathlib import Path
from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore
from core.base import ModuloBase
from core.dicom_engine import DicomEngine
from .ui import TomografiaUI
from .viewers import VolumeViewerWidget


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
        self._carregar_configuracoes_projeto()

    def _carregar_configuracoes_projeto(self):
        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        if not path_info.exists(): return
        try:
            with open(path_info, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.caminho_dicom = dados.get("caminhos", {}).get("dicom")
                if self.caminho_dicom:
                    self.ui.edit_dicom.setText(self.caminho_dicom)
        except Exception:
            pass

    def _acao_buscar_pasta(self):
        pasta = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecionar Pasta DICOM")
        if pasta: self.ui.edit_dicom.setText(pasta)

    def _acao_validar_dicom(self):
        caminho = self.ui.edit_dicom.text()
        if Path(caminho).exists() and list(Path(caminho).glob("*.dcm")):
            self.caminho_dicom = caminho
            self.ui.update_status_validado()
        else:
            self.ui.update_status_erro()
            QtWidgets.QMessageBox.warning(None, "Erro", "Pasta inválida.")

    def _acao_carregar_dicom(self):
        if not self.caminho_dicom: return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)
            if sucesso:
                self._is_initialized = True
                if self.viewer:
                    # RE-CONECTA AQUI POR SEGURANÇA
                    try:
                        self.viewer.sliceChanged.disconnect()
                    except:
                        pass
                    self.viewer.sliceChanged.connect(self._sincronizar_fatia)

                    self.viewer.set_volume(self.engine.vtk_volume)
                    self.ui.update_status_carregado()
            else:
                QtWidgets.QMessageBox.critical(None, "Erro", msg)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def _sincronizar_fatia(self, plano: str, valor: int):
        # PRINT DE EMERGÊNCIA - Se isso não aparecer, o sinal não chegou aqui.
        print(f">>> SINCRONIZANDO: {plano} -> {valor}")
        if self.viewer:
            self.viewer.update_slice(plano, valor)
            pane = self.viewer.vistas.get(plano)
            if pane:
                pane.slider.blockSignals(True)
                pane.slider.setValue(valor)
                pane.slider.blockSignals(False)

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.viewer: self.viewer.cleanup()
        self.viewer = VolumeViewerWidget()
        self.viewer.sliceChanged.connect(self._sincronizar_fatia)
        return self.viewer

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return self.ui.setup_toolboxes(
            on_buscar=self._acao_buscar_pasta,
            on_validar=self._acao_validar_dicom,
            on_carregar=self._acao_carregar_dicom,
            on_threshold=lambda v: self.viewer.update_threshold(v) if self.viewer else None,
            on_finalizar=lambda: self.concluido.emit() if self._is_initialized else None
        )