from __future__ import annotations

import sys
import os
import logging
import json
import vtk
from pathlib import Path
from typing import Dict, Optional, Any
from PySide6 import QtWidgets, QtCore


from modules.base_module.base_module import ModuloBase
from core.components.toolbars.tomography_toolbar_2 import TomographyToolbar

# Volume
from domain.volume.dicom.engines.dicom_engine import DicomEngine
from domain.volume.visualization.volume_viewer.volume_viewer_widget import VolumeViewerWidget
from domain.volume.dicom.validators.dicom_validator import DicomValidator

# Scene
from application.scene.events.event_bus import EventBus
from application.scene.registry.actor_registry import ActorRegistry

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")



class Modulo(ModuloBase):
    id = "tomography"
    nome = "Tomografia"

    def __init__(self, context: Any, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, parent=parent)

        self.project_service = getattr(context, "project_service", None)
        self.scene_manager = getattr(context, "scene_manager", None)
        self.event_bus = getattr(context, "event_bus", None)
        self.object_registry = getattr(context, "object_registry", None)

        self.app_context = context

        self.engine = DicomEngine(event_bus=self.event_bus)
        self.toolbar_handler = None
        self.viewer = None
        self.pasta_paciente: Optional[str] = None
        self.caminho_dicom: Optional[str] = None

        # Conecta o listener do EventBus para capturar o carregamento via ferramentas/pipeline
        if self.event_bus and hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("DICOM_LOADED", self._on_dicom_loaded_event)

    def get_central_area(self) -> QtWidgets.QWidget:
        if self.viewer is None:
            self.viewer = VolumeViewerWidget(
                context=self,
                event_bus=self.event_bus,
                object_registry=self.object_registry
            )
            self.viewer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        return self.viewer

    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        if self.toolbar_handler is None:
            if tool_manager and self.app_context and not hasattr(self.app_context, "tool_manager"):
                setattr(self.app_context, "tool_manager", tool_manager)

            self.toolbar_handler = TomographyToolbar(app_context=self.app_context)
            self.toolbar_handler.initialize()

        return self.toolbar_handler

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        return {}

    def configure_resources(self, caminho_paciente: str) -> None:
        """Método chamado pelo ModuloBase.inicializar() do Workspace."""
        self.pasta_paciente = caminho_paciente
        self._load_project_configs()

        if self.caminho_dicom:
            self._validate_dicom()

    def cleanup(self) -> None:
        if self.event_bus and hasattr(self.event_bus, "unsubscribe"):
            try:
                self.event_bus.unsubscribe("DICOM_LOADED", self._on_dicom_loaded_event)
            except Exception:
                pass

        if self.viewer:
            try:
                if hasattr(self.viewer, "deleteLater"):
                    self.viewer.deleteLater()
            except RuntimeError:
                pass
            self.viewer = None

        self.engine = None
        self.toolbar_handler = None
        logger.info(f"Cleanup do módulo {self.nome} executado com sucesso.")

    # --- Lógica Interna ---
    def _load_project_configs(self):
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

    def _validate_dicom(self):
        if not self.caminho_dicom or not self.pasta_paciente:
            return

        try:
            validador = DicomValidator(event_bus=getattr(self, 'event_bus', None))
            caminho_path = Path(self.caminho_dicom)
            resultado = validador.validate_directory(caminho_path)

            if resultado.get("sucesso", False):
                if self.toolbar_handler and hasattr(self.toolbar_handler, 'set_validation_state'):
                    self.toolbar_handler.set_validation_state(True)

                # Converte explicitamente para Path ao chamar o engine
                sucesso, volume_model = self.engine.load_folder(caminho_path)
                if sucesso and volume_model and self.viewer:
                    self.viewer.set_volume(volume_model.image_data)
                    self._generate_vti(volume_model.image_data)
            else:
                logger.warning(f"Diretório DICOM inválido: {resultado.get('erro', 'Desconhecido')}")
        except Exception as e:
            logger.error(f"Erro durante a validação DICOM: {e}")

    def _on_dicom_loaded_event(self, **kwargs):
        """Callback acionado globalmente quando uma nova tomografia é importada com sucesso."""
        volume_model = kwargs.get("volume")
        path_str = kwargs.get("path")

        if path_str:
            self.caminho_dicom = path_str

        if volume_model and self.viewer:
            # Se o volume passado for o image_data direto ou o modelo completo, tratamos ambos
            image_data = getattr(volume_model, "image_data", volume_model)
            self.viewer.set_volume(image_data)
            self._generate_vti(image_data)

        if self.toolbar_handler and hasattr(self.toolbar_handler, 'set_validation_state'):
            self.toolbar_handler.set_validation_state(True)

    def _generate_vti(self, vtk_image_data):
        if not vtk_image_data or not self.pasta_paciente:
            return
        try:
            pasta_projeto = Path(self.pasta_paciente) / "projeto"
            pasta_projeto.mkdir(parents=True, exist_ok=True)

            path_vti = pasta_projeto / "volume.vti"
            writer = vtk.vtkXMLImageDataWriter()
            writer.SetFileName(str(path_vti))
            writer.SetInputData(vtk_image_data)
            writer.Write()
            logger.info(f"Volume VTI gerado com sucesso em: {path_vti}")
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo VTI: {e}")

    def _wl_manual(self, window, level):
        if self.viewer:
            self.viewer.update_window_level(window, level)

    def _finalizar_etapa(self):
        pass


if __name__ == "__main__":
    from PySide6.QtCore import QEvent
    from core.components.bases.base_component import AppContext


    class DebugEventFilter(QtCore.QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.MouseButtonPress:
                print(
                    f"🖱️ [DEBUG CLIQUE] Mouse pressionado em: {obj} (Texto/Nome: {getattr(obj, 'text', lambda: 'N/A')()})")
            return super().eventFilter(obj, event)


    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    filter_inst = DebugEventFilter()
    app.installEventFilter(filter_inst)

    path_teste = os.path.abspath("./debug_paciente")
    os.makedirs(os.path.join(path_teste, "projeto"), exist_ok=True)


    class InteractiveMockToolManager:
        def __init__(self):
            self.tools = {}
            self.active_tool = None

        def get_tool(self, key):
            tool = self.tools.get(key)
            print(f"🔍 [ToolManager] Solicitou ferramenta: '{key}' -> Retornou: {tool}")
            return tool

        def register_tool(self, *args):
            if len(args) == 2:
                self.tools[args[0]] = args[1]
                print(f"✅ [ToolManager] Registrada tool por chave: {args[0]}")
            elif len(args) == 1:
                tool = args[0]
                if hasattr(tool, "name"):
                    self.tools[tool.name] = tool
                    print(f"✅ [ToolManager] Registrada tool por objeto: {tool.name}")

        def activate_tool(self, tool):
            self.active_tool = tool
            print(f"🚀 [ToolManager] ATIVANDO FERRAMENTA: {getattr(tool, 'name', tool)}")
            if hasattr(tool, "on_activate"):
                try:
                    tool.on_activate()
                    print(f"✨ [ToolManager] Tool '{getattr(tool, 'name', tool)}' executada com sucesso!")
                except Exception as e:
                    print(f"❌ [ERRO NA TOOL] Falha ao executar '{getattr(tool, 'name', tool)}': {e}")


    class MockSettings:
        def get(self, key, default=None): return default
        def set(self, key, value): pass


    contexto_mock = AppContext(
        tool_manager=InteractiveMockToolManager(),
        scene_manager=None,
        settings=MockSettings(),
        event_bus=EventBus()
    )

    setattr(contexto_mock, "object_registry", ActorRegistry())
    setattr(contexto_mock, "project_service", None)

    modulo = Modulo(context=contexto_mock)
    modulo.inicializar(path_teste)

    janela_teste = QtWidgets.QMainWindow()
    janela_teste.setWindowTitle(f"Debug Mode Interativo: {modulo.nome}")
    janela_teste.resize(1200, 800)

    toolbar = modulo.get_workspace_toolbar()
    if toolbar:
        janela_teste.addToolBar(toolbar)

    janela_teste.setCentralWidget(modulo.get_central_area())
    janela_teste.show()

    try:
        sys.exit(app.exec())
    finally:
        modulo.cleanup()