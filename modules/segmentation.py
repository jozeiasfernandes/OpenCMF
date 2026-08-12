import logging
from typing import Dict, Optional, Any
from PySide6 import QtWidgets

from modules.base_module.base_module import ModuloBase

from application.scene.events.scene_events import SceneEvents
from application.scene.utils.factory import SceneObjectFactory

from domain.volume.segmentation.engines.segmentation_engine import ThresholdSegmentationEngine

from core.components.side_panel.segmentation_sidepanel import Segmentation_SidePanel
from core.components.central_area.viewer_3d_dicom_central_area import Viewer3D_Dicom_Widget_CentralArea

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo(ModuloBase):
    def __init__(self, context: Any, parent: Optional[QtWidgets.QWidget] = None, **kwargs):
        super().__init__(context=context, parent=parent)

        self.nome = "segmentation"
        self.id = "modulo.segmentacao"

        # Extração de dependências do contexto ou kwargs se fornecidos
        self.scene_manager = kwargs.get("scene_manager") or getattr(context, "scene_manager", None)
        self.event_bus = kwargs.get("event_bus") or getattr(context, "event_bus", None)

        viewer_registry = kwargs.get("viewer_registry") or getattr(context, "viewer_registry", None)
        if viewer_registry is None:
            class DummyRegistry:
                def register(self, *args, **kwargs): pass

            self.viewer_registry = DummyRegistry()
        else:
            self.viewer_registry = viewer_registry

        self.engine_seg = ThresholdSegmentationEngine()

        self.widget_seg = Segmentation_SidePanel(context=context)

        self.widget_central = Viewer3D_Dicom_Widget_CentralArea(
            context=context,
            title="Visualizador 3D",
            cor="#2c3e50",
            event_bus=self.event_bus,
            viewer_registry=self.viewer_registry
        )

        self.widget_central.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.widget_central.setMinimumSize(400, 300)

        # Define o volume_viewer principal para a ModuloBase gerenciar
        self.viewer = self.widget_central

        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_seg.solicitarMascara.connect(self._executar_threshold)
        self.widget_seg.solicitarExportarSTL.connect(self._executar_exportacao_stl)

    # --- Implementação / Sobrescrita ---
    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna os painéis laterais (toolboxes) do módulo."""
        toolboxes = super().get_side_panel()
        toolboxes["Ferramentas"] = self.widget_seg
        return toolboxes

    def inicializar(self, caminho_paciente: str) -> None:
        """Inicializa o módulo com o caminho do paciente."""
        super().inicializar(caminho_paciente)
        logger.info(f"Módulo '{self.nome}' inicializado com paciente: {caminho_paciente}")
        # Aqui você pode carregar dados iniciais no engine_seg se necessário, ex: self.engine_seg.carregar(caminho_paciente)

    def cleanup(self) -> None:
        """Limpeza segura de widgets evitando erros de C++/Shiboken."""
        for w in [self.widget_seg, self.widget_central]:
            if w:
                try:
                    import shiboken6
                    if shiboken6.isValid(w):
                        w.deleteLater()
                except (RuntimeError, ImportError):
                    pass

        self.widget_seg = None
        self.widget_central = None
        self.viewer = None
        super().cleanup()
        logger.info(f"Módulo '{self.nome}' limpo com sucesso.")

    # --- Lógica Interna ---
    def _executar_threshold(self):
        if not self.scene_manager:
            logger.warning("Scene manager não disponível para executar o threshold.")
            return
        polydata = self.engine_seg.get_polydata()
        novo_obj = SceneObjectFactory.create_mesh_object("Segmentação", polydata)
        self.scene_manager.add_object(novo_obj)
        if self.event_bus:
            self.event_bus.emit(SceneEvents.OBJECT_ADDED, {"object": novo_obj})
        else:
            EventBus.emit(SceneEvents.OBJECT_ADDED, {"object": novo_obj})

    def _executar_exportacao_stl(self):
        pass


if __name__ == "__main__":
    import sys
    from unittest.mock import MagicMock
    from core.components.bases.base_component import AppContext
    from core.components.bases.base_tool.tool_manager import ToolManager
    from application.scene.events import EventBus
    from core.workspace.workspace_manager import WorkspaceManager
    from models.module_factory import ModuleFactory
    from layout.layout import ModuleDistributor

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Criação de um contexto completo que satisfaz todas as exigências do BaseComponent
    contexto_mock = AppContext(
        scene_manager=MagicMock(),
        tool_manager=ToolManager(),
        event_bus=EventBus()
    )

    ModuleFactory.register("modulo.segmentacao", Modulo)
    ModuleFactory.set_context(contexto_mock)

    window = WorkspaceManager()
    window.setWindowTitle("OpenCMF - Teste do Módulo de Segmentação")
    window.resize(1200, 800)

    modulo_instancia = ModuleFactory.create("modulo.segmentacao")
    if modulo_instancia:
        modulo_instancia.inicializar("./debug_paciente")
        ModuleDistributor.distribute(
            modulo_instancia,
            window.toolbar_manager,
            window.side_manager,
            window.central_manager
        )

    window.show()
    sys.exit(app.exec())