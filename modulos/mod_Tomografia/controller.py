# Controller.py
import json
from pathlib import Path
from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore
from core.base import ModuloBase
from core.dicom_engine import DicomEngine
from .ui import TomografiaUI
from core.manager import VolumeViewerWidget



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
            QtWidgets.QMessageBox.warning(None, "Erro", "Pasta inválida ou sem arquivos .dcm")

    def _acao_carregar_dicom(self):
        if not self.caminho_dicom: return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)
            if sucesso:
                self._is_initialized = True
                if self.viewer:
                    self.viewer.set_volume(self.engine.vtk_volume)
                    self.ui.update_status_carregado()
            else:
                QtWidgets.QMessageBox.critical(None, "Erro", msg)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def _sincronizar_fatia(self, plano: str, valor: int):
        """Chamado quando o slider da Janela2D ou scroll do mouse muda."""
        if self.viewer:
            self.viewer.update_slice(plano, valor)

    def _sincronizar_window_level_ui(self, window: float, level: float):
        """
        Sincronismo Inverso: Usuário arrastou o mouse na imagem ->
        Atualiza os Sliders/Spins na barra lateral (UI).
        """
        # Em vez de self.ui.blockSignals (que não existe),
        # acessamos o widget que contém os controles de brilho.
        # Assumindo que na sua UI os controles estão dentro de um layout ou widget principal:
        if hasattr(self.ui, 'group_wl'): # Substitua 'group_wl' pelo nome do seu container de W/L
            self.ui.group_wl.blockSignals(True)
            self.ui.update_wl_ui(window, level)
            self.ui.group_wl.blockSignals(False)
        else:
            # Se não houver um container, atualizamos diretamente.
            # O update_wl_ui da sua classe UI deve ser robusto o suficiente.
            self.ui.update_wl_ui(window, level)

    def _acao_wl_manual(self, window: float, level: float):
        """
        Sincronismo Direto: Usuário moveu os sliders na barra lateral ->
        Atualiza o brilho/contraste no VolumeViewer.
        """
        if self.viewer:
            self.viewer.update_window_level(window, level)

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.viewer:
            self.viewer.cleanup()

        self.viewer = VolumeViewerWidget()

        # Conexões principais
        self.viewer.sliceChanged.connect(self._sincronizar_fatia)

        # Conecta o sinal de Window/Level que o Manager emite
        self.viewer.windowLevelChanged.connect(self._sincronizar_window_level_ui)

        return self.viewer

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return self.ui.setup_toolboxes(
            on_buscar=self._acao_buscar_pasta,
            on_validar=self._acao_validar_dicom,
            on_carregar=self._acao_carregar_dicom,
            on_wl_manual=self._acao_wl_manual,
            on_finalizar=lambda: self.concluido.emit() if self._is_initialized else None
        )