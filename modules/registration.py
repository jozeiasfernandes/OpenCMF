import sys
import os
import logging
import vtk
import uuid
from pathlib import Path
from typing import Optional, Dict

from PySide6 import QtWidgets, QtCore, QtGui

from core.base_module.base import ModuloBase
from core.scene.scene_object import SceneObject
from core.scene.scene_state import SceneState
from core.scene.scene_manager import SceneManager
from core.scene.events.scene_events import (
    REGISTRATION_IMPORT_REQUESTED,
    INTERACTION_MODE_CHANGED
)
from core.scene.events.event_bus import EventBus
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.selection.selection_manager import SelectionManager
from core.scene.persistence.serializer import Serializer
from core.assets.object_manager import ObjectManager
from core.components.central_area.window_registration import WindowRegistration
from core.components.toolboxes.object_manager_toolbox import ObjetoManagerWidget
from core.components.toolboxes.registration_toolbox import Component as RegistrationToolbox
from core.components.toolboxes.objetct_properties_toolbox import Component as PropertiesComponent
from core.components.toolbars.registration_toolbar import Component as RegistrationToolbar


logger = logging.getLogger("OpenCMF.RegistrationModule")

class Modulo(ModuloBase):
    def __init__(self, scene_manager: Optional[SceneManager] = None):
        super().__init__()
        self.nome = "Alinhar objetos"
        self.id = "modulo.registration"
        self._toolbar: Optional[QtWidgets.QToolBar] = None
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
        self.widget_reg.targetChanged.connect(lambda oid: self._carregar_na_vista_por_id(oid, "A"))
        self.widget_reg.sourceChanged.connect(lambda oid: self._carregar_na_vista_por_id(oid, "B"))
        self.view_registration.requisitarCarregamentoObjeto.connect(self._on_requisicao_central_carregamento)
        self.view_registration.pontoAdicionado.connect(self.widget_reg.adicionar_ponto_tabela)
        self.widget_objetos.objetoToggled.connect(self._on_visibility_toggled)
        self.widget_objetos.opacityChanged.connect(self._on_opacity_changed_ui)
        self.widget_objetos.colorChanged.connect(self._on_color_changed_ui)
        self.scene_manager.events.subscribe(INTERACTION_MODE_CHANGED, self._on_interaction_mode_changed)

    def _on_interaction_mode_changed(self, mode: str):
        if hasattr(self.view_registration, "set_interaction_mode"):
            self.view_registration.set_interaction_mode(mode)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.object_manager = ObjectManager(caminho_paciente, self.serializer)
        self.object_manager.object_added.connect(self._on_scene_object_added)
        self.object_manager.object_removed.connect(self.scene_manager.remove_object)
        self.scene_manager.state.set_patient(caminho_paciente)
        self.widget_objetos.set_patient_path(caminho_paciente)
        self.view_registration.connect_properties_panel(self.widget_propriedades)
        self.object_manager.load_patient_data()
        QtCore.QTimer.singleShot(0, self._sincronizar_cena_inicial)

    def _sincronizar_cena_inicial(self):
        for obj in self.scene_manager.objects.all():
            self.scene_manager.update_visibility(obj.id, obj.visible)
        self._atualizar_ui_combos()

    def get_workspace(self) -> QtWidgets.QWidget:
        return self.view_registration

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        if not self._toolbar:
            self._toolbar = RegistrationToolbar(scene_manager=self.scene_manager)
            self.scene_manager.events.subscribe(REGISTRATION_IMPORT_REQUESTED, self._on_import_request)
        return self._toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Alinhar Objetos": self.widget_reg,
            "Objetos": self.widget_objetos,
            "Propriedades": self.widget_propriedades
        }

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

        self.scene_manager.update_visibility(obj.id, obj.visible)
        self._atualizar_ui_combos()

    def _atualizar_ui_combos(self):
        objs = [{"id": o.id, "name": o.name} for o in self.scene_manager.objects.all()]
        self.widget_reg.atualizar_combos(objs)
        self.view_registration.atualizar_lista_objetos([o['name'] for o in objs])

    def _on_visibility_toggled(self, oid: str, visible: bool):
        self.scene_manager.update_visibility(oid, visible)
        obj = self.scene_manager.get_object(oid)
        if obj:
            obj.visible = visible
            self.object_manager.save_scene(self.scene_manager.objects.all())

    def _on_opacity_changed_ui(self, oid: str, opacity: float):
        self.scene_manager.update_opacity(oid, opacity)
        obj = self.scene_manager.get_object(oid)
        if obj:
            obj.opacity = opacity
            self.object_manager.save_scene(self.scene_manager.objects.all())

    def _on_color_changed_ui(self, oid: str, color: QtGui.QColor):
        rgb = (color.redF(), color.greenF(), color.blueF())
        self.scene_manager.update_color(oid, rgb)
        obj = self.scene_manager.get_object(oid)
        if obj:
            obj.color = rgb
            self.object_manager.save_scene(self.scene_manager.objects.all())

    def _on_requisicao_central_carregamento(self, vista_id, nome):
        obj = next((o for o in self.scene_manager.objects.all() if o.name == nome), None)
        if obj:
            combo = self.widget_reg.combo_target if vista_id == "A" else self.widget_reg.combo_source
            combo.blockSignals(True)
            combo.setCurrentText(nome)
            combo.blockSignals(False)
            self._carregar_na_vista(obj, vista_id)

    def _carregar_na_vista_por_id(self, oid, vista):
        obj = self.scene_manager.get_object(oid)
        if obj:
            self._carregar_na_vista(obj, vista)

    def _carregar_na_vista(self, obj: SceneObject, vista: str):
        full_path = Path(self.pasta_paciente) / obj.file_path
        if not full_path.exists():
            return
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(full_path))
        reader.Update()
        if vista == "A":
            self.view_registration.adicionar_malha_vista_a(obj.name, reader.GetOutput(), obj_id=obj.id)
        else:
            self.view_registration.adicionar_malha_vista_b(obj.name, reader.GetOutput(), obj_id=obj.id)

    def _executar_registro(self):
        logger.info("Executando registro...")

    def _resetar_pontos(self):
        self.view_registration.limpar_marcadores()
        self.widget_reg.limpar_tabela()

if __name__ == "__main__":
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