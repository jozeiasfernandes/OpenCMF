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

        # --- LOG DE DEBUG PARA O CONSTRUTOR ---
        if self.event_bus and hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("DICOM_LOADED", self._on_dicom_loaded_event)
            logger.info("🟢 [Modulo Tomografia] Inscrito com sucesso no evento 'DICOM_LOADED'.")
        else:
            logger.warning(
                "⚠️ [Modulo Tomografia] event_bus não está disponível ou não possui método 'subscribe' no __init__!")

    def get_central_area(self) -> QtWidgets.QWidget:
        if self.viewer is None:
            ctx = getattr(self, "app_context", self)
            self.viewer = VolumeViewerWidget(
                context=ctx,
                event_bus=getattr(ctx, "event_bus", self.event_bus),
                object_registry=getattr(ctx, "object_registry", self.object_registry)
            )
            self.viewer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            logger.info("📺 [Modulo Tomografia] VolumeViewerWidget criado e instanciado na área central.")

        return self.viewer

    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        if self.toolbar_handler is None:
            if tool_manager and self.app_context:
                setattr(self.app_context, "tool_manager", tool_manager)

            self.toolbar_handler = TomographyToolbar(app_context=self.app_context)
            self.toolbar_handler.initialize()
            logger.info("🛠️ [Modulo Tomografia] TomographyToolbar inicializada.")

        return self.toolbar_handler

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        return {}

    def configure_resources(self, caminho_paciente: str) -> None:
        """Método chamado pelo ModuloBase.inicializar() do Workspace."""
        self.pasta_paciente = caminho_paciente
        logger.info(f"📂 [Modulo Tomografia] Configurando recursos para o paciente: {caminho_paciente}")
        self._load_project_configs()

        if self.caminho_dicom:
            self._validate_dicom()

    def cleanup(self) -> None:
        if self.event_bus and hasattr(self.event_bus, "unsubscribe"):
            try:
                self.event_bus.unsubscribe("DICOM_LOADED", self._on_dicom_loaded_event)
                logger.info("🔴 [Modulo Tomografia] Desinscrito do evento 'DICOM_LOADED'.")
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
        logger.info(f"🧹 Cleanup do módulo {self.nome} executado com sucesso.")

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
                    logger.info(f"📄 [Modulo Tomografia] Caminho DICOM carregado do info.json: {self.caminho_dicom}")
            except Exception as e:
                logger.error(f"❌ [Modulo Tomografia] Erro ao carregar info.json: {e}")
        else:
            logger.warning(f"⚠️ [Modulo Tomografia] Arquivo info.json não encontrado em: {path_info}")

    def _validate_dicom(self):
        if not self.caminho_dicom or not self.pasta_paciente:
            logger.warning("⚠️ [Modulo Tomografia] _validate_dicom abortado: caminho_dicom ou pasta_paciente ausentes.")
            return

        try:
            validador = DicomValidator(event_bus=getattr(self, 'event_bus', None))
            caminho_path = Path(self.caminho_dicom)
            logger.info(f"🔍 [Modulo Tomografia] Validando diretório DICOM: {caminho_path}")
            resultado = validador.validate_directory(caminho_path)

            if resultado.get("sucesso", False):
                logger.info("✅ [Modulo Tomografia] Diretório DICOM validado com sucesso!")
                if self.toolbar_handler and hasattr(self.toolbar_handler, 'set_validation_state'):
                    self.toolbar_handler.set_validation_state(True)

                sucesso, volume_model = self.engine.load_folder(caminho_path)
                if sucesso and volume_model and self.viewer:
                    logger.info("🚀 [Modulo Tomografia] Volume carregado pelo engine e injetado diretamente no viewer.")
                    self.viewer.set_volume(volume_model.image_data)
                    self._generate_vti(volume_model.image_data)
            else:
                logger.warning(
                    f"⚠️ [Modulo Tomografia] Diretório DICOM inválido: {resultado.get('erro', 'Desconhecido')}")
        except Exception as e:
            logger.error(f"❌ [Modulo Tomografia] Erro crítico durante a validação DICOM: {e}")

    def _on_dicom_loaded_event(self, **kwargs):
        """Callback acionado globalmente quando uma nova tomografia é importada com sucesso."""
        logger.info(f"🎯 [Modulo Tomografia] Evento 'DICOM_LOADED' capturado com argumentos keys: {list(kwargs.keys())}")

        volume_model = kwargs.get("volume")
        path_str = kwargs.get("path")

        if path_str:
            self.caminho_dicom = path_str

        if volume_model and self.viewer:
            image_data = getattr(volume_model, "image_data", volume_model)
            logger.info(f"✨ [Modulo Tomografia] Repassando dados de imagem para o VolumeViewerWidget.")
            self.viewer.set_volume(image_data)
            self._generate_vti(image_data)
        else:
            logger.warning(
                f"⚠️ [Modulo Tomografia] Evento 'DICOM_LOADED' recebido, mas 'volume' ou 'viewer' estão ausentes. (volume: {volume_model}, viewer: {self.viewer})")

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
            logger.info(f"💾 [Modulo Tomografia] Volume VTI gerado com sucesso em: {path_vti}")
        except Exception as e:
            logger.error(f"❌ [Modulo Tomografia] Erro ao gerar arquivo VTI: {e}")

    def _wl_manual(self, window, level):
        if self.viewer:
            self.viewer.update_window_level(window, level)

    def _complete_stage(self):
        pass


if __name__ == "__main__":
    from PySide6.QtCore import QEvent
    from core.components.bases.base_component import AppContext

    class DebugEventFilter(QtCore.QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.MouseButtonPress:
                print(f"🖱️ [DEBUG CLIQUE] Mouse pressionado em: {obj} (Texto/Nome: {getattr(obj, 'text', lambda: 'N/A')()})")
            return super().eventFilter(obj, event)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    filter_inst = DebugEventFilter()
    app.installEventFilter(filter_inst)

    path_teste = os.path.abspath("./debug_paciente")
    os.makedirs(os.path.join(path_teste, "projeto"), exist_ok=True)

    class InteractiveMockToolManager:
        def __init__(self, context_ref):
            self.tools = {}
            self.active_tool = None
            self.context_ref = context_ref

        def get_tool(self, key):
            tool = self.tools.get(key)
            print(f"🔍 [ToolManager] Solicitou ferramenta: '{key}' -> Retornou: {tool}")
            if tool and hasattr(tool, "context") and not tool.context:
                tool.context = self.context_ref
            return tool

        def register_tool(self, *args):
            if len(args) == 2:
                tool = args[1]
                if hasattr(tool, "context"):
                    tool.context = self.context_ref
                self.tools[args[0]] = tool
                print(f"✅ [ToolManager] Registrada tool por chave: {args[0]}")
            elif len(args) == 1:
                tool = args[0]
                if hasattr(tool, "context"):
                    tool.context = self.context_ref
                if hasattr(tool, "name"):
                    self.tools[tool.name] = tool
                    print(f"✅ [ToolManager] Registrada tool por objeto: {tool.name}")

        def activate_tool(self, tool):
            self.active_tool = tool
            print(f"🚀 [ToolManager] ATIVANDO FERRAMENTA: {getattr(tool, 'name', tool)}")
            if tool and hasattr(tool, "context") and not tool.context:
                tool.context = self.context_ref
            if hasattr(tool, "on_activate"):
                try:
                    tool.on_activate()
                    print(f"✨ [ToolManager] Tool '{getattr(tool, 'name', tool)}' executada com sucesso!")
                except Exception as e:
                    print(f"❌ [ERRO NA TOOL] Falha ao executar '{getattr(tool, 'name', tool)}': {e}")

    class MockSettings:
        def get(self, key, default=None): return default
        def set(self, key, value): pass

    event_bus_inst = EventBus()

    contexto_mock = AppContext(
        tool_manager=None,
        scene_manager=None,
        settings=MockSettings(),
        event_bus=event_bus_inst
    )

    tool_manager_mock = InteractiveMockToolManager(contexto_mock)
    contexto_mock.tool_manager = tool_manager_mock

    setattr(contexto_mock, "object_registry", ActorRegistry())
    setattr(contexto_mock, "project_service", None)

    # Instancia o módulo PRIMEIRO para que as referências existam
    modulo = Modulo(context=contexto_mock)

    setattr(modulo, "event_bus", event_bus_inst)
    setattr(contexto_mock, "event_bus", event_bus_inst)

    modulo.inicializar(path_teste)

    janela_teste = QtWidgets.QMainWindow()
    janela_teste.setWindowTitle(f"Debug Mode Interativo: {modulo.nome}")
    janela_teste.resize(1200, 800)

    setattr(janela_teste, "event_bus", event_bus_inst)
    if hasattr(modulo, "scene"):
        setattr(janela_teste, "scene", modulo.scene)
        setattr(contexto_mock, "scene", modulo.scene)
    setattr(contexto_mock, "window", janela_teste)

    toolbar = modulo.get_workspace_toolbar()
    if toolbar:
        janela_teste.addToolBar(toolbar)

    janela_teste.setCentralWidget(modulo.get_central_area())
    janela_teste.show()

    try:
        sys.exit(app.exec())
    finally:
        modulo.cleanup()