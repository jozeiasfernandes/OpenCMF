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
from core.scene.persistence.serializer import Serializer
from core.assets.patient_file_manager import ObjectManager

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

        self.view_registration = WindowRegistration()
        self.widget_reg = RegistrationToolbox()
        self.widget_objetos = ObjetoManagerWidget()
        self.widget_propriedades = PropertiesComponent(self)

        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_reg.solicitarAlinhamento.connect(self._executar_registro)
        self.widget_reg.limparPontos.connect(self._resetar_pontos)
        self.widget_reg.targetChanged.connect(self._on_target_combo_changed)
        self.widget_reg.sourceChanged.connect(self._on_source_combo_changed)

        self.view_registration.requisitarCarregamentoObjeto.connect(self._on_requisicao_central_carregamento)
        self.view_registration.pontoAdicionado.connect(self.widget_reg.adicionar_ponto_tabela)

        self.widget_objetos.objetoToggled.connect(self._on_objeto_toggled)
        self.widget_objetos.opacityChanged.connect(self._on_opacity_changed)
        self.widget_objetos.colorChanged.connect(self._on_color_changed)
        self.widget_objetos.deleteRequested.connect(self._on_delete_requested)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)

        self.object_manager = ObjectManager(caminho_paciente, self.serializer)
        self.object_manager.object_added.connect(self._on_scene_object_added)
        self.object_manager.load_patient_data()

        self.widget_objetos.set_patient_path(caminho_paciente)
        self.view_registration.connect_properties_panel(self.widget_propriedades)

    def get_workspace(self) -> QtWidgets.QWidget:
        return self.view_registration

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        if self._toolbar is None:
            self._toolbar = RegistrationToolbar()
            h = self._toolbar.handler
            h.importRequested.connect(self._fluxo_importacao)
            h.deletePointRequested.connect(self.view_registration.remover_ultimo_marcador)
            h.pointSizeChanged.connect(self.view_registration.set_ponto_raio)
            h.resetLayoutRequested.connect(self.view_registration.reset_layout_vistas)
        return self._toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Alinhar Objetos": self.widget_reg,
            "Objetos": self.widget_objetos,
            "Propriedades": self.widget_propriedades
        }

    def _fluxo_importacao(self, categoria: str, subcategoria: str):
        file_filter = "Arquivos Suportados (*.stl *.vti *.obj);;STL (*.stl);;VTK XML (*.vti)"
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.view_registration, "Selecionar Arquivo", "", file_filter
        )

        if path:
            obj_id = str(uuid.uuid4())
            self.object_manager.import_external_file(path, categoria, obj_id)

    def _on_scene_object_added(self, obj: SceneObject):
        self.widget_objetos.adicionar_objeto_lista(
            obj.name, obj.type, QtGui.QColor.fromRgbF(*obj.color), objeto_id=obj.id
        )

        nomes_objetos = [o.name for o in self.object_manager.objects.values()]
        self.widget_reg.atualizar_combos(nomes_objetos)
        self.view_registration.atualizar_lista_objetos(nomes_objetos)

    def _on_requisicao_central_carregamento(self, vista_id, nome):
        combo = self.widget_reg.combo_target if vista_id == "A" else self.widget_reg.combo_source
        combo.blockSignals(True)
        combo.setCurrentText(nome)
        combo.blockSignals(False)

        if vista_id == "A":
            self._on_target_combo_changed(nome)
        else:
            self._on_source_combo_changed(nome)

    def _on_target_combo_changed(self, nome: str):
        obj = next((o for o in self.object_manager.objects.values() if o.name == nome), None)
        if obj:
            self._carregar_na_vista(obj, "A")

    def _on_source_combo_changed(self, nome: str):
        obj = next((o for o in self.object_manager.objects.values() if o.name == nome), None)
        if obj:
            self._carregar_na_vista(obj, "B")

    def _carregar_na_vista(self, obj: SceneObject, vista: str):
        full_path = Path(self.pasta_paciente) / obj.file_path
        if not full_path.exists():
            return

        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(full_path))
        reader.Update()

        if vista == "A":
            self.view_registration.adicionar_malha_vista_a(obj.name, reader.GetOutput())
        else:
            self.view_registration.adicionar_malha_vista_b(obj.name, reader.GetOutput())

    def _on_objeto_toggled(self, nome, visivel):
        self.view_registration.set_objeto_visibilidade(nome, visivel)

    def _on_opacity_changed(self, nome, valor):
        self.view_registration.set_objeto_opacidade(nome, valor)

    def _on_color_changed(self, nome, color):
        rgb = (color.redF(), color.greenF(), color.blueF())
        self.view_registration.set_objeto_cor(nome, rgb)

    def _on_delete_requested(self, nome):
        self.view_registration.remover_objeto(nome)

    def _executar_registro(self):
        pts_a = self.view_registration.get_points_a()
        pts_b = self.view_registration.get_points_b()

        if len(pts_a) < 3 or len(pts_a) != len(pts_b):
            QtWidgets.QMessageBox.warning(self.view_registration, "Aviso", "Selecione pontos correspondentes.")
            return

        logger.info("Executando registro...")

    def _resetar_pontos(self):
        self.view_registration.limpar_marcadores()
        self.widget_reg.limpar_tabela()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    test_path = os.path.abspath("./teste_paciente")

    modulo = Modulo()
    modulo.inicializar(test_path)

    window = QtWidgets.QMainWindow()
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