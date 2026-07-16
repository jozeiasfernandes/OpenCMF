import logging
import json
import vtk
from pathlib import Path
from typing import Dict, Optional, Any
from PySide6 import QtWidgets, QtCore

from core.volume.dicom_engine import DicomEngine
from core.volume.viewer import VolumeViewerWidget
from core.volume.validator import DicomValidator
from core.components.bases.base_toolbar import BaseToolbar
from core.components.toolbars.tomography_toolbar import TomographyToolbar
from core.workspace.contracts import IModule

from core.scene.events.event_bus import EventBus
from core.scene.registry.actor_registry import ActorRegistry

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(IModule):
    def __init__(self, pasta_paciente: Optional[str] = None,
                 event_bus: Optional[Any] = None,
                 actor_registry: Optional[Any] = None,
                 **kwargs):
        super().__init__()

        self.nome = "Tomografia"
        self.id = "modulo.tomografia"

        self.pasta_paciente = pasta_paciente or kwargs.get("pasta_paciente")
        self.event_bus = event_bus or kwargs.get("event_bus")
        self.actor_registry = actor_registry or kwargs.get("actor_registry")
        self.project_service = kwargs.get("project_service")

        self.engine = DicomEngine()
        self.toolbar_handler: Optional[TomographyToolbar] = None
        self.viewer: Optional[VolumeViewerWidget] = None
        self.caminho_dicom: Optional[str] = None
        self._is_initialized = False

        if self.pasta_paciente:
            self._carregar_configs_projeto()

    def get_main_widget(self) -> QtWidgets.QWidget:
        """Contrato IModule: Retorna o widget central (Viewer)."""
        if self.viewer is None:
            # Use os atributos definidos no __init__, não o getattr
            self.viewer = VolumeViewerWidget(
                event_bus=self.event_bus,
                object_registry=self.actor_registry # Aqui estava o erro
            )

            if self.engine.vtk_volume:
                self.viewer.set_volume(self.engine.vtk_volume)

        return self.viewer

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        # Criamos o objeto toolbar (QToolBar) e instanciamos nossa TomographyToolbar nele
        toolbar = QtWidgets.QToolBar("Tomografia")
        self.toolbar_handler = TomographyToolbar(parent=toolbar, context=self)

        # Conexões diretas caso necessário
        if hasattr(self.toolbar_handler, 'btn_load'):
            self.toolbar_handler.btn_load.clicked.connect(self._carregar_dicom)

        return toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        # Como a UI foi removida, retornamos um dicionário vazio
        return {}

    def cleanup(self) -> None:
        if self.viewer:
            self.viewer.deleteLater()
            self.viewer = None
        self.engine = None
        self.toolbar_handler = None
        print(f"Cleanup do módulo {self.nome} executado.")

    # --- Lógica Interna ---
    def _carregar_configs_projeto(self):
        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        if path_info.exists():
            with open(path_info, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.caminho_dicom = dados.get("caminhos", {}).get("dicom")

    def _buscar_pasta(self):
        settings = QtCore.QSettings("OpenCMF", "Config")
        pasta = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecione DICOM", settings.value("ultimo_dir", ""))
        if pasta:
            settings.setValue("ultimo_dir", pasta)
            self.caminho_dicom = pasta

    def _validar_dicom(self):
        if not self.caminho_dicom: return
        validador = DicomValidator(self.pasta_paciente)
        resultado = validador.analisar_caminho(self.caminho_dicom)

        if resultado["sucesso"] and self.toolbar_handler:
            # Substitua o método por um que exista na sua nova Toolbar
            if hasattr(self.toolbar_handler, 'set_validation_state'):
                self.toolbar_handler.set_validation_state(True)

    def _carregar_dicom(self):
        if not self.caminho_dicom: return
        sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)
        if sucesso and self.viewer:
            self.viewer.set_volume(self.engine.vtk_volume)

    def _gerar_vti(self):
        if not self.engine.vtk_volume: return
        path_vti = Path(self.pasta_paciente) / "projeto" / "volume.vti"
        writer = vtk.vtkXMLImageDataWriter()
        writer.SetFileName(str(path_vti))
        writer.SetInputData(self.engine.vtk_volume)
        writer.Write()

    def _wl_manual(self, window, level):
        if self.viewer: self.viewer.update_window_level(window, level)

    def _finalizar_etapa(self):
        pass


if __name__ == "__main__":
    import sys
    import os
    from core.scene.events.event_bus import EventBus
    from core.scene.registry.actor_registry import ActorRegistry

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    path_teste = os.path.abspath("./debug_paciente")
    os.makedirs(os.path.join(path_teste, "projeto"), exist_ok=True)
    bus = EventBus()
    registry = ActorRegistry()
    modulo = Modulo(
        pasta_paciente=path_teste,
        event_bus=bus,
        actor_registry=registry
    )
    janela_teste = QtWidgets.QMainWindow()
    janela_teste.setWindowTitle(f"Debug Mode: {modulo.nome}")
    janela_teste.resize(1200, 800)

    janela_teste.addToolBar(modulo.get_workspace_toolbar())
    janela_teste.setCentralWidget(modulo.get_main_widget())
    janela_teste.show()
    try:
        sys.exit(app.exec())
    finally:
        modulo.cleanup()