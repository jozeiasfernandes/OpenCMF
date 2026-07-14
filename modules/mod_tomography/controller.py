import json
import vtk
from pathlib import Path
from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore

from core.volume.dicom_engine import DicomEngine
from core.volume.viewer import VolumeViewerWidget
from core.volume.validator import DicomValidator
from modules.mod_tomography.ui import TomografiaUI
from core.components.bases.base_toolbar import BaseToolbar
from core.components.toolbars.tomography_toolbar import TomographyToolbar
from core.workspace.contracts import IModule


class Modulo(IModule):
    def __init__(self, pasta_paciente: str):
        self.nome = "Tomografia"
        self.id = "modulo.tomografia"
        self.pasta_paciente = pasta_paciente

        self.engine = DicomEngine()
        self.ui = TomografiaUI()

        self.toolbar_handler: Optional[TomographyToolbar] = None
        self.viewer: Optional[VolumeViewerWidget] = None
        self.caminho_dicom: Optional[str] = None
        self._is_initialized = False

        self._carregar_configs_projeto()

    def get_main_widget(self) -> QtWidgets.QWidget:
        """Contrato IModule: Retorna o widget central (Viewer)."""
        if self.viewer is None:
            self.viewer = VolumeViewerWidget()
            self.viewer.windowLevelChanged.connect(self.ui.update_wl_ui)

            if self.engine.vtk_volume:
                self.viewer.set_volume(self.engine.vtk_volume)

        return self.viewer

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        """Contrato IModule: Retorna a toolbar do módulo."""
        toolbar = QtWidgets.QToolBar("Tomografia")

        # CORREÇÃO: Passando 'self' (o módulo atual) como contexto para a Toolbar.
        # Certifique-se de que a classe TomographyToolbar aceita esse argumento no __init__.
        self.toolbar_handler = TomographyToolbar(parent=toolbar, context=self)

        # Conexões
        self.toolbar_handler.importDicomRequested.connect(self._buscar_pasta)
        self.toolbar_handler.validateRequested.connect(self._validar_dicom)
        self.toolbar_handler.loadVolumeRequested.connect(self._carregar_dicom)
        self.toolbar_handler.exportVtiRequested.connect(self._gerar_vti)

        # Conexões de View
        self.toolbar_handler.resetViewRequested.connect(
            lambda: self.viewer.refresh_display() if self.viewer else None
        )
        self.toolbar_handler.layoutChanged.connect(
            lambda l: self.viewer.configurar_layout(l) if self.viewer else None
        )
        self.toolbar_handler.colorMapChanged.connect(
            lambda l: self.viewer.apply_global_lut(l) if self.viewer else None
        )

        return toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """Contrato IModule: Retorna os painéis laterais."""
        return self.ui.setup_toolboxes(
            on_buscar=self._buscar_pasta,
            on_validar=self._validar_dicom,
            on_carregar=self._carregar_dicom,
            on_gerar_vti=self._gerar_vti,
            on_wl_manual=self._wl_manual,
            on_finalizar=self._finalizar_etapa
        )

    def cleanup(self) -> None:
        """Contrato IModule: Limpeza essencial para evitar memory leaks."""
        if self.viewer:
            self.viewer.deleteLater()
            self.viewer = None

        self.engine = None
        self.toolbar_handler = None
        print(f"Cleanup do módulo {self.nome} executado.")

    # --- Lógica Interna (Mantida, porém desacoplada de Dialogs globais) ---
    def _carregar_configs_projeto(self):
        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        if path_info.exists():
            with open(path_info, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.caminho_dicom = dados.get("caminhos", {}).get("dicom")
                if self.caminho_dicom:
                    self.ui.edit_dicom.setText(self.caminho_dicom)

    def _buscar_pasta(self):
        settings = QtCore.QSettings("OpenCMF", "Config")
        pasta = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecione DICOM", settings.value("ultimo_dir", ""))
        if pasta:
            self.ui.edit_dicom.setText(pasta)
            settings.setValue("ultimo_dir", pasta)
            self.caminho_dicom = pasta

    def _validar_dicom(self):
        # AQUI: Substitua o uso de QProgressDialog por chamadas ao StatusBarManager
        # Exemplo: self.status_bar.set_message("Validando...")
        validador = DicomValidator(self.pasta_paciente)
        resultado = validador.analisar_caminho(self.ui.edit_dicom.text())

        if not resultado["sucesso"]:
            return  # Notifique via sistema de logs/status central

        self.ui.update_status_validado()
        if self.toolbar_handler: self.toolbar_handler.set_validation_state(True)

    def _carregar_dicom(self):
        if not self.caminho_dicom: return
        sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)
        if sucesso and self.viewer:
            self.viewer.set_volume(self.engine.vtk_volume)
            self.ui.update_status_carregado()

    def _gerar_vti(self):
        # Mova esta lógica para um QThread se o arquivo for grande
        path_vti = Path(self.pasta_paciente) / "projeto" / "volume.vti"
        writer = vtk.vtkXMLImageDataWriter()
        writer.SetFileName(str(path_vti))
        writer.SetInputData(self.engine.vtk_volume)
        writer.Write()
        self._is_initialized = True
        self.ui.update_status_vti_gerado()

    def _wl_manual(self, window, level):
        if self.viewer: self.viewer.update_window_level(window, level)

    def _finalizar_etapa(self):
        # Emite sinal para o gerenciador de workspace avançar a etapa
        pass

class TomographyToolbar(BaseToolbar):
    def __init__(self, parent, context=None):
        super().__init__(context=context, title="Tomografia", parent=parent)


if __name__ == "__main__":
    import sys
    import os
    from PySide6 import QtWidgets, QtCore

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    path_teste = os.path.abspath("./debug_paciente")
    os.makedirs(os.path.join(path_teste, "projeto"), exist_ok=True)

    modulo = Modulo(pasta_paciente=path_teste)

    janela_teste = QtWidgets.QMainWindow()
    janela_teste.setWindowTitle(f"Debug Mode: {modulo.nome}")
    janela_teste.resize(1200, 800)

    janela_teste.addToolBar(modulo.get_workspace_toolbar())
    janela_teste.setCentralWidget(modulo.get_main_widget())

    # Dock com ferramentas
    dock = QtWidgets.QDockWidget("Ferramentas", janela_teste)
    container_tabs = QtWidgets.QTabWidget()

    toolboxes = modulo.get_toolboxes()
    for nome, widget in toolboxes.items():
        container_tabs.addTab(widget, nome)

    dock.setWidget(container_tabs)
    janela_teste.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    janela_teste.show()

    try:
        sys.exit(app.exec())
    finally:
        modulo.cleanup()