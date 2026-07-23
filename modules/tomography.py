import sys
import os
import logging
import json
import vtk
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Any
from PySide6 import QtWidgets, QtCore

from core.volume.dicom_engine import DicomEngine
from core.volume.viewer import VolumeViewerWidget
from core.volume.validator import DicomValidator
from core.components.toolbars.tomography_toolbar import TomographyToolbar

from core.scene.events.event_bus import EventBus
from core.scene.registry.actor_registry import ActorRegistry
from modules.base_module.base_module import ModuloBase

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(ModuloBase):
    id = "modulo.tomografia"
    nome = "Tomografia"

    def __init__(self, context: Any, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, parent=parent)

        self.project_service = getattr(context, "project_service", None)
        self.scene_manager = getattr(context, "scene_manager", None)
        self.event_bus = getattr(context, "event_bus", None)
        self.object_registry = getattr(context, "object_registry", None)

        self.app_context = context

        self.engine = DicomEngine()
        self.toolbar_handler = None
        self.viewer = None
        self.pasta_paciente: Optional[str] = None
        self.caminho_dicom: Optional[str] = None

    def get_main_widget(self) -> QtWidgets.QWidget:
        if self.viewer is None:
            self.viewer = VolumeViewerWidget(
                context=self,
                event_bus=self.event_bus,
                object_registry=self.object_registry
            )

            if self.viewer.layout() is None:
                self.viewer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        return self.viewer

    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        if self.toolbar_handler is None:
            self.toolbar_handler = TomographyToolbar(app_context=self.app_context)
            self.toolbar_handler.initialize()

            if hasattr(self.toolbar_handler, 'btn_load'):
                self.toolbar_handler.btn_load.clicked.connect(self._carregar_dicom)

        return self.toolbar_handler

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {}

    def configurar_recursos(self, caminho_paciente: str) -> None:
        """Método chamado pelo ModuloBase.inicializar() do Workspace."""
        self.pasta_paciente = caminho_paciente
        self._carregar_configs_projeto()

    def cleanup(self) -> None:
        if self.viewer:
            self.viewer.deleteLater()
            self.viewer = None
        self.engine = None
        self.toolbar_handler = None
        print(f"Cleanup do módulo {self.nome} executado.")

    # --- Lógica Interna ---
    def _carregar_configs_projeto(self):
        if not self.pasta_paciente:
            return
        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        if path_info.exists():
            try:
                with open(path_info, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    self.caminho_dicom = dados.get("caminhos", {}).get("dicom")
            except Exception as e:
                logger.error(f"Erro ao carregar info.json: {e}")

    def _buscar_pasta(self):
        settings = QtCore.QSettings("OpenCMF", "Config")
        pasta = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecione DICOM", settings.value("ultimo_dir", ""))
        if pasta:
            settings.setValue("ultimo_dir", pasta)
            self.caminho_dicom = pasta

    def _validar_dicom(self):
        if not self.caminho_dicom or not self.pasta_paciente:
            return
        validador = DicomValidator(self.pasta_paciente)
        resultado = validador.analisar_caminho(self.caminho_dicom)

        if resultado.get("sucesso") and self.toolbar_handler:
            if hasattr(self.toolbar_handler, 'set_validation_state'):
                self.toolbar_handler.set_validation_state(True)

    def _carregar_dicom(self):
        if not self.caminho_dicom:
            self._buscar_pasta()
            if not self.caminho_dicom:
                return

        sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)
        if sucesso and self.viewer:
            self.viewer.set_volume(self.engine.vtk_volume)
        else:
            logger.error(f"Falha ao carregar DICOM: {msg}")

    def _gerar_vti(self):
        if not self.engine.vtk_volume or not self.pasta_paciente:
            return
        path_vti = Path(self.pasta_paciente) / "projeto" / "volume.vti"
        writer = vtk.vtkXMLImageDataWriter()
        writer.SetFileName(str(path_vti))
        writer.SetInputData(self.engine.vtk_volume)
        writer.Write()

    def _wl_manual(self, window, level):
        if self.viewer:
            self.viewer.update_window_level(window, level)

    def _finalizar_etapa(self):
        pass


if __name__ == "__main__":
    @dataclass
    class AppContext:
        tool_manager: Any
        scene_manager: Any
        settings: Any
        event_bus: Any
        object_registry: Any
        project_service: Any = None


    class MockToolManager:
        def get_tool(self, key): return None  # Corrigido de .get() para .get_tool()[cite: 1]


    class MockSettings:
        def get(self, key, default=None): return default
        def set(self, key, value): pass


    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    path_teste = os.path.abspath("./debug_paciente")
    os.makedirs(os.path.join(path_teste, "projeto"), exist_ok=True)

    contexto_mock = AppContext(
        tool_manager=MockToolManager(),
        scene_manager=None,
        settings=MockSettings(),
        event_bus=EventBus(),
        object_registry=ActorRegistry(),
        project_service=None
    )

    modulo = Modulo(context=contexto_mock)
    modulo.inicializar(path_teste)

    janela_teste = QtWidgets.QMainWindow()
    janela_teste.setWindowTitle(f"Debug Mode: {modulo.nome}")
    janela_teste.resize(1200, 800)

    toolbar = modulo.get_workspace_toolbar()
    if toolbar:
        janela_teste.addToolBar(toolbar)

    janela_teste.setCentralWidget(modulo.get_main_widget())
    janela_teste.show()

    try:
        sys.exit(app.exec())
    finally:
        modulo.cleanup()