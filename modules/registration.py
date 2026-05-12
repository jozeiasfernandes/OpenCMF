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
from core.scene.events.scene_events import REGISTRATION_IMPORT_REQUESTED
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
    def __init__(self):
        super().__init__()
        self.nome = "Alinhar objetos"
        self.id = "modulo.registration"
        self._toolbar: Optional[QtWidgets.QToolBar] = None
        self.serializer = Serializer()

        self.scene_manager = SceneManager(
            SceneState(),
            EventBus(),
            ObjectRegistry(),
            ActorRegistry(),
            SelectionManager(),
        )

        self.view_registration = WindowRegistration(scene_manager=self.scene_manager)
        self.widget_reg = RegistrationToolbox()
        self.widget_objetos = ObjetoManagerWidget()
        self.widget_propriedades = PropertiesComponent(self)

        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_reg.solicitarAlinhamento.connect(self._executar_registro)
        self.widget_reg.limparPontos.connect(self._resetar_pontos)

        self.widget_reg.targetChanged.connect(lambda obj_id: self._carregar_na_vista_por_id(obj_id, "A"))
        self.widget_reg.sourceChanged.connect(lambda obj_id: self._carregar_na_vista_por_id(obj_id, "B"))

        self.view_registration.requisitarCarregamentoObjeto.connect(self._on_requisicao_central_carregamento)
        self.view_registration.pontoAdicionado.connect(self.widget_reg.adicionar_ponto_tabela)

        self.widget_objetos.objetoToggled.connect(
            lambda oid, vis: self.scene_manager.update_visibility(oid, vis)
        )
        self.widget_objetos.opacityChanged.connect(
            lambda oid, val: self.scene_manager.update_opacity(oid, val)
        )
        self.widget_objetos.colorChanged.connect(self._on_color_changed_via_scene)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.object_manager = ObjectManager(caminho_paciente, self.serializer)
        self.object_manager.object_added.connect(self._on_scene_object_added)
        self.object_manager.object_removed.connect(self._on_object_removed_from_scene)

        self._clear_registration_scene_objects()
        self.object_manager.load_patient_data()

        self.scene_manager.state.set_patient(caminho_paciente)
        self.scene_manager.sync_state()
        self.widget_objetos.set_patient_path(caminho_paciente)
        self.view_registration.connect_properties_panel(self.widget_propriedades)

    def get_workspace(self) -> QtWidgets.QWidget:
        return self.view_registration

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        if self._toolbar is None:
            self._toolbar = RegistrationToolbar(scene_manager=self.scene_manager)
            self.scene_manager.events.subscribe(
                REGISTRATION_IMPORT_REQUESTED,
                self._on_registration_import_requested,
            )
        return self._toolbar

    def _on_registration_import_requested(self, **kwargs) -> None:
        category = kwargs.get("category") or ""
        subcategory = kwargs.get("subcategory") or ""
        self._fluxo_importacao(category, subcategory)
    def _clear_registration_scene_objects(self) -> None:
        for obj in list(self.scene_manager.objects.all()):
            self.scene_manager.remove_object(obj.id)

    def _on_color_changed_via_scene(self, id_obj: str, color: QtGui.QColor) -> None:
        self.scene_manager.update_color(
            id_obj, (color.redF(), color.greenF(), color.blueF())
        )

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Alinhar Objetos": self.widget_reg,
            "Objetos": self.widget_objetos,
            "Propriedades": self.widget_propriedades
        }

    def _fluxo_importacao(self, categoria: str, subcategoria: str):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.view_registration,
            "Selecionar Arquivo",
            "",
            "Malhas (*.stl *.obj)"
        )
        if path:
            obj_id = uuid.uuid4().hex[:12]
            self.object_manager.import_external_file(path, categoria, obj_id)

    def _on_scene_object_added(self, obj: SceneObject):
        self.scene_manager.add_object(obj)
        self.widget_objetos.adicionar_objeto_lista(
            obj.name, obj.type, QtGui.QColor.fromRgbF(*obj.color), objeto_id=obj.id
        )
        objs_data = [{"id": o.id, "name": o.name} for o in self.object_manager.objects.values()]
        self.widget_reg.atualizar_combos(objs_data)
        self.view_registration.atualizar_lista_objetos([o['name'] for o in objs_data])

    def _on_object_removed_from_scene(self, obj_id: str) -> None:
        self.scene_manager.remove_object(obj_id)

    def _scene_object_by_name(self, nome: str) -> Optional[SceneObject]:
        for o in self.scene_manager.objects.all():
            if o.name == nome:
                return o
        return None

    def _on_requisicao_central_carregamento(self, vista_id, nome):
        obj = self._scene_object_by_name(nome)
        if obj is None and getattr(self, "object_manager", None):
            obj = next(
                (o for o in self.object_manager.objects.values() if o.name == nome),
                None,
            )
        if obj:
            combo = self.widget_reg.combo_target if vista_id == "A" else self.widget_reg.combo_source
            combo.blockSignals(True)
            combo.setCurrentText(nome)
            combo.blockSignals(False)
            self._carregar_na_vista(obj, vista_id)

    def _carregar_na_vista_por_id(self, id_obj, vista):
        obj = self.scene_manager.get_object(id_obj)
        if obj is None and getattr(self, "object_manager", None):
            obj = self.object_manager.objects.get(id_obj)
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
    if not os.path.exists(test_path):
        os.makedirs(test_path)

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