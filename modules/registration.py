import vtk
import sys
import os
import logging
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from core.base_module.base import ModuloBase
from core.components.central_area.window_registration import WindowRegistration
from core.components.toolboxes.object_manager_toolbox import ObjetoManagerWidget
from core.components.toolboxes.registration_toolbox import Component
from core.components.toolboxes.objetct_properties_toolbox import Component as PropertiesComponent
from core.components.toolbars.registration_toolbar import Component as RegistrationToolbar
from core.imports.object_manager import ObjectManager

logger = logging.getLogger("RegistrationModule")


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Alinhar objetos"
        self.id = "modulo.registration"
        self.pasta_paciente = None
        self.object_manager: Optional[ObjectManager] = None

        self.view_registration = WindowRegistration()
        self.view_registration.setMinimumSize(0, 0)

        self.widget_reg = Component()
        self.widget_reg.setMinimumSize(0, 0)
        self.widget_reg.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred      # Preferred: não força expansão vertical
        )

        self.widget_objetos = ObjetoManagerWidget()
        self.widget_objetos.setMinimumSize(0, 0)
        self.widget_objetos.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )

        self.widget_propriedades = PropertiesComponent(self)
        self.widget_propriedades.setMinimumSize(0, 0)
        self.widget_propriedades.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )

        self._toolbar: Optional[QtWidgets.QToolBar] = None  # cache — nunca recriar

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
        self.widget_objetos.nomeAlterado.connect(self._on_nome_alterado)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.object_manager = ObjectManager(caminho_paciente)
        self.object_manager.object_added.connect(self._on_object_added_manager)
        self.object_manager.load_existing_objects()

        self.widget_objetos.set_patient_path(caminho_paciente)
        if hasattr(self.widget_propriedades, 'set_patient_path'):
            self.widget_propriedades.set_patient_path(caminho_paciente)

        self.widget_objetos.objetoSelecionado.connect(self._on_objeto_selecionado)
        self.view_registration.connect_properties_panel(self.widget_propriedades)

    # --- Interface pública ---

    def get_workspace(self) -> QtWidgets.QWidget:
        return self.view_registration

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        if self._toolbar is not None:            # cache: nunca recriar nem reconectar sinais
            return self._toolbar

        toolbar = RegistrationToolbar()
        toolbar.setMinimumSize(0, 0)
        toolbar.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed          # altura fixa — nunca empurra o layout
        )

        h = toolbar.handler
        h.importRequested.connect(lambda: self._importar_objeto("surfaces", "Importado"))
        h.deletePointRequested.connect(self.view_registration.remover_ultimo_marcador)
        h.pointSizeChanged.connect(self.view_registration.set_ponto_raio)
        h.resetLayoutRequested.connect(self.view_registration.reset_layout_vistas)

        self._toolbar = toolbar
        return self._toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Alinhar Objetos": self.widget_reg,
            "Objetos": self.widget_objetos,
            "Propriedades": self.widget_propriedades
        }

    # --- Carregamento e sincronização ---

    def _on_requisicao_central_carregamento(self, vista_id, nome):
        if vista_id == "A":
            self.widget_reg.combo_target.blockSignals(True)
            self.widget_reg.combo_target.setCurrentText(nome)
            self.widget_reg.combo_target.blockSignals(False)
            self._on_target_combo_changed(nome)
        else:
            self.widget_reg.combo_source.blockSignals(True)
            self.widget_reg.combo_source.setCurrentText(nome)
            self.widget_reg.combo_source.blockSignals(False)
            self._on_source_combo_changed(nome)

    def _on_target_combo_changed(self, nome: str):
        if not nome:
            return
        props = next((p for p in self.object_manager.objects.values() if p.name == nome), None)
        if props:
            self._carregar_na_vista(props, "A")

    def _on_source_combo_changed(self, nome: str):
        if not nome:
            return
        props = next((p for p in self.object_manager.objects.values() if p.name == nome), None)
        if props:
            self._carregar_na_vista(props, "B")

    def _carregar_na_vista(self, props, vista: str):
        path = Path(self.pasta_paciente) / props.file_path
        if not path.exists():
            logger.error(f"Arquivo não encontrado: {path}")
            return

        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(path))
        reader.Update()

        polydata = reader.GetOutput()
        if vista == "A":
            self.view_registration.adicionar_malha_vista_a(props.name, polydata)
        else:
            self.view_registration.adicionar_malha_vista_b(props.name, polydata)

    # --- Gerenciamento de objetos ---

    def _on_object_added_manager(self, props):
        categoria = self._mapear_categoria_para_tipo(props.type)
        self.widget_objetos.adicionar_objeto_lista(
            props.name, categoria, props.render["color"], objeto_id=props.id
        )
        nomes_objetos = [obj.name for obj in self.object_manager.objects.values()]
        self.widget_reg.atualizar_combos(nomes_objetos)
        self.view_registration.atualizar_lista_objetos(nomes_objetos)

    def _on_objeto_toggled(self, nome, visivel):
        if not visivel:
            self.view_registration.remover_objeto(nome)
        else:
            if nome == self.widget_reg.get_target_name():
                self._on_target_combo_changed(nome)
            elif nome == self.widget_reg.get_source_name():
                self._on_source_combo_changed(nome)

    def _on_opacity_changed(self, nome, valor):
        self.view_registration.set_objeto_opacidade(nome, valor)

    def _on_color_changed(self, nome, color):
        rgb = (color.redF(), color.greenF(), color.blueF())
        self.view_registration.set_objeto_cor(nome, rgb)

    def _on_delete_requested(self, nome):
        self.view_registration.remover_objeto(nome)

    def _on_nome_alterado(self, nome_original: str, novo_nome: str) -> None:
        for props in self.object_manager.objects.values():
            if props.name == nome_original:
                props.name = novo_nome
                break
        nomes = [obj.name for obj in self.object_manager.objects.values()]
        self.widget_reg.atualizar_combos(nomes)
        self.view_registration.atualizar_lista_objetos(nomes)

    # --- Operações ---

    def _executar_registro(self):
        pts_a = self.view_registration.get_points_a()
        pts_b = self.view_registration.get_points_b()
        if len(pts_a) < 3 or len(pts_a) != len(pts_b):
            QtWidgets.QMessageBox.warning(
                self.view_registration, "Aviso",
                "Marque pelo menos 3 pontos correspondentes em cada vista."
            )
            return
        logger.info(f"Iniciando registro com {len(pts_a)} pontos.")

    def _resetar_pontos(self):
        self.view_registration.limpar_marcadores()
        self.widget_reg.limpar_tabela()

    def _importar_objeto(self, categoria: str, subcategoria: str) -> None:
        if not self.object_manager:
            return
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.view_registration, "Importar STL", "", "STL (*.stl)"
        )
        if path:
            self.object_manager.import_object(path, categoria, subcategoria)

    def _mapear_categoria_para_tipo(self, tipo_pasta: str) -> str:
        return {
            "surfaces": "Superfícies",
            "photos": "Fotografias",
            "volume": "Volume",
            "implants": "Implantes"
        }.get(tipo_pasta, "Outros")

    def _on_objeto_selecionado(self, nome_objeto: str) -> None:
        if hasattr(self.widget_propriedades, 'load_object_properties'):
            self.widget_propriedades.load_object_properties(nome_objeto)


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