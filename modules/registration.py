import vtk
import sys
import os
import logging
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore,QtGui

from core.base_module.base import ModuloBase
from core.components.central_area.window_registration import WindowRegistration
from core.components.toolboxes.object_manager_toolbox import ObjetoManagerWidget
from core.components.toolboxes.registration_toolbox import Component
from core.components.toolbars.registration_toolbar import Component as RegistrationToolbar
from core.imports.object_manager import ObjectManager

os.environ["VTK_SILENT_ERRORS"] = "1"
vtk.vtkObject.GlobalWarningDisplayOff()

logger = logging.getLogger("RegistrationModule")


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Alinhar objetos"
        self.id = "modulo.registration"
        self.object_manager: Optional[ObjectManager] = None

        self.view_registration = WindowRegistration()
        self.widget_reg = Component()
        self.widget_objetos = ObjetoManagerWidget()

        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_reg.solicitarAlinhamento.connect(self._executar_registro)
        self.widget_reg.limparPontos.connect(self._resetar_pontos)
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

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        toolbar = RegistrationToolbar()
        h = toolbar.handler

        h.importRequested.connect(lambda: self._importar_objeto("Superfícies", "Importado"))
        h.deletePointRequested.connect(self.view_registration.remover_ultimo_marcador)
        h.pointSizeChanged.connect(self.view_registration.set_ponto_raio)
        h.resetLayoutRequested.connect(self.view_registration.reset_layout_vistas)

        return toolbar

    def get_workspace(self) -> QtWidgets.QWidget:
        return self.view_registration

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Alinhar Objetos": self.widget_reg,
            "Objetos": self.widget_objetos
        }

    def _importar_objeto(self, categoria: str, subcategoria: str) -> None:
        if not self.object_manager:
            QtWidgets.QMessageBox.warning(
                self.view_registration,
                "Módulo não inicializado",
                "O módulo ainda não foi inicializado. Tente clicar na aba do módulo novamente."
            )
            return

        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.view_registration, "Selecionar Malha", "", "Malhas (*.stl *.obj *.ply)"
        )
        if path:
            self.object_manager.import_object(path, categoria, subcategoria)

    def _on_object_added_manager(self, props):
        categoria_mapeada = self._mapear_categoria_para_tipo(props.type)
        self.widget_objetos.adicionar_objeto_lista(
            props.name,
            categoria_mapeada,
            props.render["color"],
            objeto_id=props.id
        )
        self.widget_reg.atualizar_combos([obj.name for obj in self.object_manager.objects.values()])

    def _mapear_categoria_para_tipo(self, tipo_pasta: str) -> str:
        mapeamento = {
            "surfaces": "Superfícies",
            "photos": "Fotografias",
            "volume": "Volume",
            "others": "Outros"
        }
        return mapeamento.get(tipo_pasta, "Outros")

    def _on_objeto_toggled(self, nome, visivel):
        if not visivel:
            self.view_registration.remover_objeto(nome)
            return

        props = next((p for p in self.object_manager.objects.values() if p.name == nome), None)
        if not props:
            return

        path = Path(self.pasta_paciente) / props.file_path
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(path))
        reader.Update()

        if nome == self.widget_reg.get_target_name():
            self.view_registration.adicionar_malha_vista_a(nome, reader.GetOutput())
        else:
            self.view_registration.adicionar_malha_vista_b(nome, reader.GetOutput())

    def _on_opacity_changed(self, nome, valor):
        self.view_registration.set_objeto_opacidade(nome, valor)

    def _on_color_changed(self, nome, color):
        rgb = (color.redF(), color.greenF(), color.blueF())
        self.view_registration.set_objeto_cor(nome, rgb)

    def _on_delete_requested(self, nome):
        self.view_registration.remover_objeto(nome)
        restantes = [obj.name for obj in self.object_manager.objects.values() if obj.name != nome]
        self.widget_reg.atualizar_combos(restantes)

    def _on_nome_alterado(self, nome_original: str, novo_nome: str) -> None:
        props = next((p for p in self.object_manager.objects.values() if p.name == nome_original), None)
        if props:
            props.name = novo_nome
            logger.info(f"Objeto renomeado: {nome_original} -> {novo_nome}")
            self.widget_reg.atualizar_combos([obj.name for obj in self.object_manager.objects.values()])

    def _executar_registro(self):
        pts_a = self.view_registration.get_points_a()
        pts_b = self.view_registration.get_points_b()

        if len(pts_a) < 3 or len(pts_a) != len(pts_b):
            QtWidgets.QMessageBox.warning(None, "Erro", "Selecione a mesma quantidade de pontos (mín. 3).")
            return

        print(f"Executando registro: {len(pts_a)} pares.")

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