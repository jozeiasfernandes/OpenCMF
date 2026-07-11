import logging
import uuid
import vtk
from pathlib import Path
from typing import Optional, Dict

from PySide6 import QtWidgets, QtCore, QtGui

from modules.base_module.base_module import ModuloBase
from core.scene.scene_object import SceneObject
from core.scene.scene_state import SceneState
from core.scene.scene_manager import SceneManager
from core.scene.events.event_bus import EventBus
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.selection.selection_manager import SelectionManager
from core.scene.persistence.serializer import Serializer
from core.scene.events.scene_events import SceneEvents, RegistrationEvents
from core.scene.io.importer import ObjectImporter

from core.components.central_area.window_registration import WindowRegistration
from core.components.toolboxes.object_manager_toolbox import ObjetoManagerWidget
from core.components.toolboxes.objetct_properties_toolbox import AxisSliderRow
from core.components.toolbars.registration_toolbar import RegistrationToolbarHandler

logger = logging.getLogger("OpenCMF.RegistrationModule")


class Modulo(ModuloBase):

    def __init__(self, scene_manager: Optional[SceneManager] = None):
        super().__init__(scene_manager=scene_manager)

        self.nome = "Alinhar objetos"
        self.id = "modulo.registration"

        self._toolbar_widget: Optional[QtWidgets.QToolBar] = None
        self.serializer = Serializer()

        self.scene_manager = scene_manager or self._criar_scene_manager_padrao()

        self.widget_reg = WindowRegistration(scene_manager=self.scene_manager)
        self.widget_objetos = ObjetoManagerWidget()
        self.widget_propriedades = AxisSliderRow(
            label="Z",
            min_val=0.0,
            max_val=100.0,
            default=50.0,
            color="#4b4bff"
        )

        self._conectar_sinais()

    # ==================== Configuração inicial ====================

    def _criar_scene_manager_padrao(self) -> SceneManager:
        bus = EventBus()
        state = SceneState()
        base_patient_path = "C:/OpenCMF/data/default_patient"
        importer = ObjectImporter(patient_path=base_patient_path)

        return SceneManager(
            state=state,
            event_bus=bus,
            object_registry=ObjectRegistry(),
            actor_registry=ActorRegistry(),
            selection_manager=SelectionManager(event_bus=bus, state=state),
            importer=importer
        )

    def _conectar_sinais(self):
        """Conecta os sinais do gerenciador de cena."""
        self.scene_manager.events.subscribe(RegistrationEvents.ALIGNMENT_REQUESTED, self._executar_registro)
        self.scene_manager.events.subscribe(RegistrationEvents.CLEAR_POINTS, self._resetar_pontos)
        self.scene_manager.events.subscribe(RegistrationEvents.TARGET_CHANGED,
                                            lambda object_id: self._carregar_na_vista_por_id(object_id, "A"))
        self.scene_manager.events.subscribe(RegistrationEvents.SOURCE_CHANGED,
                                            lambda object_id: self._carregar_na_vista_por_id(object_id, "B"))
        self.scene_manager.events.subscribe(SceneEvents.INTERACTION_MODE_CHANGED,
                                            self._on_interaction_mode_changed)

    # ==================== Handlers de eventos ====================

    def _on_interaction_mode_changed(self, mode: str):
        if hasattr(self.widget_reg, "set_interaction_mode"):
            self.widget_reg.set_interaction_mode(mode)

    def _carregar_na_vista_por_id(self, oid: str, vista: str):
        obj = self.scene_manager.get_object(oid)
        if obj:
            self._carregar_na_vista(obj, vista)

    def _carregar_na_vista(self, obj: SceneObject, vista: str):
        full_path = Path(self.pasta_paciente) / obj.file_path
        if not full_path.exists():
            logger.error(f"Arquivo não encontrado: {full_path}")
            return

        ext = full_path.suffix.lower()
        if ext == ".stl":
            reader = vtk.vtkSTLReader()
        elif ext == ".obj":
            reader = vtk.vtkOBJReader()
        elif ext == ".vti":
            reader = vtk.vtkXMLImageDataReader()
        else:
            logger.warning(f"Formato não suportado automaticamente: {ext}")
            return

        reader.SetFileName(str(full_path))
        reader.Update()
        poly_data = reader.GetOutput()

        if not poly_data or poly_data.GetNumberOfPoints() == 0:
            logger.error(f"O arquivo {full_path} está vazio ou corrompido.")
            return

        if vista == "A":
            self.view_registration.adicionar_malha_vista_a(obj.name, poly_data, obj_id=obj.id)
        else:
            self.view_registration.adicionar_malha_vista_b(obj.name, poly_data, obj_id=obj.id)

        logger.info(f"Objeto {obj.name} carregado com sucesso na Vista {vista}")

    def _on_scene_object_added(self, obj: SceneObject):
        if not self.scene_manager.objects.has(obj.id):
            self.scene_manager.add_object(obj)

        if hasattr(obj, 'file_path') and obj.file_path:
            self._carregar_na_vista(obj, "A")
            self._carregar_na_vista(obj, "B")

        self.widget_objetos.adicionar_objeto_lista(
            obj.name,
            obj.type,
            QtGui.QColor.fromRgbF(*obj.color),
            objeto_id=obj.id
        )
        self._atualizar_ui_combos()

    def _atualizar_ui_combos(self):
        objs = [{"id": o.id, "name": o.name} for o in self.scene_manager.objects.all()]
        self.widget_reg.atualizar_combos(objs)

    def _on_visibility_toggled(self, oid: str, visible: bool):
        self.scene_manager.update_visibility(oid, visible)
        self.object_manager.save_scene(self.scene_manager.objects.all())

    def _on_opacity_changed_ui(self, oid: str, opacity: float):
        self.scene_manager.update_opacity(oid, opacity)
        self.object_manager.save_scene(self.scene_manager.objects.all())

    def _on_color_changed_ui(self, oid: str, color: QtGui.QColor):
        rgb = (color.redF(), color.greenF(), color.blueF())
        self.scene_manager.update_color(oid, rgb)
        self.object_manager.save_scene(self.scene_manager.objects.all())

    def _on_import_request(self, **kwargs):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Importar Malha", "", "Malhas (*.stl *.obj)"
        )
        if path:
            self.object_manager.import_external_file(
                path,
                kwargs.get("category", "models"),
                uuid.uuid4().hex[:12]
            )

    def _executar_registro(self):
        logger.info("Executando registro...")

    def _resetar_pontos(self):
        self.view_registration.limpar_marcadores()
        self.widget_reg.limpar_tabela()

    # ==================== Métodos públicos ====================

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.pasta_paciente = caminho_paciente

        self.object_manager = ObjectImporter(patient_path=caminho_paciente)

        self.object_manager.object_added.connect(self._on_scene_object_added)

        self.scene_manager.state.current_patient = caminho_paciente
        self.widget_objetos.set_patient_path(caminho_paciente)

        if hasattr(self.widget_reg, "view_registration"):
            self.widget_reg.view_registration.connect_properties_panel(self.widget_propriedades)
        else:
            logger.error("View de registro não encontrada no widget_reg!")

        if hasattr(self.object_manager, "load_patient_data"):
            self.object_manager.load_patient_data()

    def get_workspace(self) -> QtWidgets.QWidget:
        return self.get_main_widget()

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        if not self._toolbar_widget:
            self._toolbar_widget = QtWidgets.QToolBar("Ferramentas de Registro")
            self._toolbar_handler = RegistrationToolbarHandler(
                toolbar=self._toolbar_widget,
                scene_manager=self.scene_manager
            )
            self.scene_manager.events.subscribe(
                RegistrationEvents.IMPORT_REQUESTED,
                self._on_import_request
            )
        return self._toolbar_widget

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Objetos": self.widget_objetos,
            "Propriedades": self.widget_propriedades
        }

    def get_main_widget(self) -> QtWidgets.QWidget:
        return self.widget_reg


    def cleanup(self) -> None:
        logger.info("Limpando recursos do módulo de Registro...")
        super().cleanup()

    def _on_scene_object_removed(self, object_id: str):
        self.widget_objetos.remover_objeto_lista(object_id)
        self.widget_reg.view_registration.limpar_objeto(object_id)


if __name__ == "__main__":
    import sys
    import os

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    test_path = os.path.abspath("./teste_paciente")
    os.makedirs(test_path, exist_ok=True)

    modulo = Modulo()
    modulo.inicializar(test_path)

    window = QtWidgets.QMainWindow()
    window.resize(1200, 800)
    window.setCentralWidget(modulo.get_workspace())
    window.addToolBar(modulo.get_workspace_toolbar())

    dock = QtWidgets.QDockWidget("Painel de Controle")
    tabs = QtWidgets.QTabWidget()
    for titulo, widget in modulo.get_toolboxes().items():
        tabs.addTab(widget, titulo)
    dock.setWidget(tabs)

    window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    window.show()

    sys.exit(app.exec())