import logging
import uuid
import vtk
from pathlib import Path
from typing import Optional, Dict
from PySide6 import QtWidgets, QtCore, QtGui

from modules.base_module.base_module import ModuloBase
from core.scene import (
    SceneObject, SceneState, SceneManager, EventBus,
    ObjectRegistry, ActorRegistry, SelectionManager, Serializer, scene_events
)
from core.objects_manager.object_manager import ObjectManager
from core.components.central_area.window_registration import WindowRegistration
from core.components.toolboxes import (
    ObjetoManagerWidget, RegistrationToolbox, PropertiesComponent
)
from core.components.toolbars import RegistrationToolbarHandler

logger = logging.getLogger("OpenCMF.RegistrationModule")


class Modulo(ModuloBase):
    def __init__(self, scene_manager: Optional[SceneManager] = None):
        super().__init__()
        self.nome = "Alinhar objetos"
        self.id = "modulo.registration"
        self._toolbar_widget: Optional[QtWidgets.QToolBar] = None
        self.serializer = Serializer()
        self.scene_manager = scene_manager or self._criar_scene_manager_padrao()
        self.view_registration = WindowRegistration(scene_manager=self.scene_manager)
        self.widget_reg = RegistrationToolbox()
        self.widget_objetos = ObjetoManagerWidget()
        self.widget_propriedades = PropertiesComponent(self)
        self._conectar_sinais()

    def _criar_scene_manager_padrao(self) -> SceneManager:
        bus = EventBus()
        return SceneManager(
            SceneState(),
            bus,
            ObjectRegistry(),
            ActorRegistry(),
            SelectionManager(event_bus=bus),
        )

    def _conectar_sinais(self):
        self.widget_reg.solicitarAlinhamento.connect(self._executar_registro)
        self.widget_reg.limparPontos.connect(self._resetar_pontos)

        # Sinais críticos para carregar os objetos nas vistas
        self.widget_reg.targetChanged.connect(lambda oid: self._carregar_na_vista_por_id(oid, "A"))
        self.widget_reg.sourceChanged.connect(lambda oid: self._carregar_na_vista_por_id(oid, "B"))

        self.view_registration.pontoAdicionado.connect(self.widget_reg.adicionar_ponto_tabela)
        self.widget_objetos.objetoToggled.connect(self._on_visibility_toggled)
        self.widget_objetos.opacityChanged.connect(self._on_opacity_changed_ui)
        self.widget_objetos.colorChanged.connect(self._on_color_changed_ui)
        self.scene_manager.events.subscribe(scene_events.INTERACTION_MODE_CHANGED, self._on_interaction_mode_changed)

    def _carregar_na_vista_por_id(self, oid: str, vista: str):
        obj = self.scene_manager.get_object(oid)
        if obj:
            self._carregar_na_vista(obj, vista)

    def _carregar_na_vista(self, obj: SceneObject, vista: str):
        """Lógica de leitura de arquivo reintroduzida."""
        full_path = Path(self.pasta_paciente) / obj.file_path
        if not full_path.exists():
            logger.error(f"Arquivo não encontrado: {full_path}")
            return

        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(full_path))
        reader.Update()

        if vista == "A":
            self.view_registration.adicionar_malha_vista_a(obj.name, reader.GetOutput(), obj_id=obj.id)
        else:
            self.view_registration.adicionar_malha_vista_b(obj.name, reader.GetOutput(), obj_id=obj.id)

    def _on_interaction_mode_changed(self, mode: str):
        if hasattr(self.view_registration, "set_interaction_mode"):
            self.view_registration.set_interaction_mode(mode)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.pasta_paciente = caminho_paciente # Garante acesso ao caminho
        self.object_manager = ObjectManager(caminho_paciente, self.serializer)
        self.object_manager.object_added.connect(self._on_scene_object_added)
        self.object_manager.object_removed.connect(self.scene_manager.remove_object)
        self.scene_manager.state.set_patient(caminho_paciente)
        self.widget_objetos.set_patient_path(caminho_paciente)
        self.view_registration.connect_properties_panel(self.widget_propriedades)
        self.object_manager.load_patient_data()

    def get_workspace(self) -> QtWidgets.QWidget:
        return self.view_registration

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        if not self._toolbar_widget:
            # 1. Cria o widget visual QToolBar
            self._toolbar_widget = QtWidgets.QToolBar("Ferramentas de Registro")

            # 2. Cria o controlador e passa a QToolBar para ele manipular
            self._toolbar_handler = RegistrationToolbarHandler(
                toolbar=self._toolbar_widget,
                scene_manager=self.scene_manager
            )

            self.scene_manager.events.subscribe(scene_events.REGISTRATION_IMPORT_REQUESTED, self._on_import_request)

        # 3. Retorna o widget QToolBar, conforme exigido pelo QMainWindow
        return self._toolbar_widget

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Alinhar Objetos": self.widget_reg,
            "Objetos": self.widget_objetos,
            "Propriedades": self.widget_propriedades
        }

    # ... (restante dos métodos mantêm-se iguais)
    def _on_import_request(self, **kwargs):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Importar Malha", "", "Malhas (*.stl *.obj)")
        if path:
            self.object_manager.import_external_file(
                path,
                kwargs.get("category", "models"),
                uuid.uuid4().hex[:12]
            )

    def _on_scene_object_added(self, obj: SceneObject):
        if not self.scene_manager.objects.has(obj.id):
            self.scene_manager.add_object(obj)

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

    def _executar_registro(self):
        logger.info("Executando registro...")

    def _resetar_pontos(self):
        self.view_registration.limpar_marcadores()
        self.widget_reg.limpar_tabela()


if __name__ == "__main__":
    import sys, os

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