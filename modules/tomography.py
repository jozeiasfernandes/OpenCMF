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
from core.components.bases.base_toolbar import BaseToolbar, AppContext
from core.components.toolbars.tomography_toolbar import TomographyToolbar
from core.workspace.contracts import IModule

from core.scene.events.event_bus import EventBus
from core.scene.registry.actor_registry import ActorRegistry
from modules.base_module.base_module import ModuloBase

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(ModuloBase):
    def __init__(self, context: Any, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, parent=parent)

        self.nome = "Tomografia"
        self.id = "modulo.tomografia"

        self.project_service = getattr(context, "project_service", None)
        self.scene_manager = getattr(context, "scene_manager", None)
        self.event_bus = getattr(context, "event_bus", None)
        self.object_registry = getattr(context, "object_registry", None)

        self.app_context = context

        self.engine = DicomEngine()
        self.toolbar_handler = None
        self.viewer = None
        self._is_initialized = False

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

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        self.toolbar_handler = TomographyToolbar(app_context=self.app_context)

        self.toolbar_handler.initialize()

        if hasattr(self.toolbar_handler, 'btn_load'):
            self.toolbar_handler.btn_load.clicked.connect(self._carregar_dicom)

        return self.toolbar_handler

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
        if not self.caminho_dicom:
            self._buscar_pasta()
            if not self.caminho_dicom: return

        sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)
        if sucesso and self.viewer:
            self.viewer.set_volume(self.engine.vtk_volume)
        else:
            logger.error(f"Falha ao carregar DICOM: {msg}")

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
    # 1. Definindo o Contexto de Teste
    @dataclass
    class AppContext:
        tool_manager: Any
        scene_manager: Any
        settings: Any
        event_bus: Any
        object_registry: Any
        project_service: Any = None


    class MockToolManager:
        def get_tool(self, key): return None


    class MockSettings:
        def get(self, key, default=None): return default

        def set(self, key, value): pass


    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    path_teste = os.path.abspath("./debug_paciente")
    os.makedirs(os.path.join(path_teste, "projeto"), exist_ok=True)

    # 2. Montando o contexto como a Factory faria
    contexto_mock = AppContext(
        tool_manager=MockToolManager(),
        scene_manager=None,  # Aqui você passaria o seu Mock SceneManager
        settings=MockSettings(),
        event_bus=EventBus(),
        object_registry=ActorRegistry(),
        project_service=None
    )

    # 3. Instanciando o Módulo via Contexto (conforme refatoramos)
    modulo = Modulo(context=contexto_mock)

    # Executa a inicialização do Módulo (padrão que definimos)
    modulo.inicializar(path_teste)

    janela_teste = QtWidgets.QMainWindow()
    janela_teste.setWindowTitle(f"Debug Mode: {modulo.nome}")
    janela_teste.resize(1200, 800)

    # 4. Distribuição da UI
    toolbar = modulo.get_workspace_toolbar()
    if toolbar:
        janela_teste.addToolBar(toolbar)

    janela_teste.setCentralWidget(modulo.get_main_widget())

    janela_teste.show()

    try:
        sys.exit(app.exec())
    finally:
        # cleanup() limpa referências e invoca dispose() dos filhos
        modulo.cleanup()