import vtk
import sys
import os
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from core.base_module.base import ModuloBase
from core.components.central_area.window_registration import WindowRegistration
from core.components.toolboxes.object_manager_toolbox import ObjetoManagerWidget
from core.components.toolboxes.registration_toolbox import RegistrationWidget
from core.imports.object_manager import ObjectManager

os.environ["VTK_SILENT_ERRORS"] = "1"
vtk.vtkObject.GlobalWarningDisplayOff()


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Registro"
        self.id = "modulo.registration"

        self.object_manager: Optional[ObjectManager] = None
        self.view_registro: Optional[WindowRegistration] = None

        self.widget_reg = RegistrationWidget()
        self.widget_objetos = ObjetoManagerWidget()

        self._conectar_sinais_toolbox()

    def _conectar_sinais_toolbox(self):
        self.widget_reg.solicitarAlinhamento.connect(self._executar_registro_landmarking)
        self.widget_reg.limparPontos.connect(self._resetar_pontos)

        self.widget_objetos.objetoToggled.connect(self._on_objeto_toggled)
        self.widget_objetos.opacityChanged.connect(self._on_opacity_changed)
        self.widget_objetos.colorChanged.connect(self._on_color_changed)
        self.widget_objetos.deleteRequested.connect(self._on_delete_requested)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.object_manager = ObjectManager(caminho_paciente)

        if not self.view_registro:
            self.view_registro = WindowRegistration()

        self._configurar_toolbar()
        self.view_registro.pontoAdicionado.connect(self._on_ponto_adicionado_na_janela)

        self.object_manager.object_added.connect(self._on_object_added_manager)
        self.object_manager.load_existing_objects()

    def _configurar_toolbar(self):
        handler = self.view_registro.toolbar_handler
        if not handler: return

        handler.importRequested.connect(self._importar_objeto_via_manager)

        if hasattr(handler, 'deletePointRequested'):
            handler.deletePointRequested.connect(self.view_registro.remover_ultimo_ponto)

        handler.pointSizeChanged.connect(self._on_point_size_changed)

        if hasattr(handler, 'resetLayoutRequested'):
            handler.resetLayoutRequested.connect(self.view_registro.reset_layout_vistas)

    def _importar_objeto_via_manager(self, categoria, subcategoria):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.view_registro, "Selecionar Malha", "", "Malhas (*.stl *.obj *.ply)"
        )
        if path:
            self.object_manager.import_object(path, categoria, subcategoria)

    def _on_object_added_manager(self, props):
        self.widget_objetos.adicionar_objeto_lista(props.name, props.type, props.render["color"])
        self.widget_reg.atualizar_combos([obj.name for obj in self.object_manager.objects.values()])

    def _on_objeto_toggled(self, nome, visivel):
        if not visivel:
            self.view_registro.remover_objeto(nome)
            return

        props = next((p for p in self.object_manager.objects.values() if p.name == nome), None)
        if not props: return

        path = Path(self.pasta_paciente) / props.file_path
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(path))
        reader.Update()

        if nome == self.widget_reg.get_target_name():
            self.view_registro.adicionar_malha_vista_a(nome, reader.GetOutput())
        else:
            self.view_registro.adicionar_malha_vista_b(nome, reader.GetOutput())

    def _on_opacity_changed(self, nome, valor):
        if self.view_registro: self.view_registro.set_objeto_opacidade(nome, valor)

    def _on_color_changed(self, nome, color):
        if self.view_registro:
            rgb = (color.redF(), color.greenF(), color.blueF())
            self.view_registro.set_objeto_cor(nome, rgb)

    def _on_delete_requested(self, nome):
        self.view_registro.remover_objeto(nome)
        # Lógica de remoção física delegada ao manager se necessário no futuro
        self.widget_reg.atualizar_combos([obj.name for obj in self.object_manager.objects.values() if obj.name != nome])

    def _on_point_size_changed(self, size: float):
        for view in [self.view_registro.view_a, self.view_registro.view_b]:
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            for _ in range(actors.GetNumberOfItems()):
                actor = actors.GetNextActor()
                if (mapper := actor.GetMapper()) and isinstance(mapper.GetInputAlgorithm(), vtk.vtkSphereSource):
                    mapper.GetInputAlgorithm().SetRadius(size)
            view.render()

    def _on_ponto_adicionado_na_janela(self, vista, pos):
        self.widget_reg.adicionar_ponto_tabela(vista, pos)

    def _executar_registro_landmarking(self):
        pa, pb = self.view_registro.get_points_a(), self.view_registro.get_points_b()
        if len(pa) < 3 or len(pa) != len(pb):
            QtWidgets.QMessageBox.warning(None, "Erro", "Pontos insuficientes ou desbalanceados.")
            return
        print(f"Alinhando {len(pa)} pares de pontos...")

    def _resetar_pontos(self):
        self.view_registro.limpar_marcadores()
        self.widget_reg.limpar_tabela()

    def get_workspace(self) -> QtWidgets.QWidget:
        return self.view_registro

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {"Configuração": self.widget_reg, "Arquivos": self.widget_objetos}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    test_path = os.path.abspath("./teste_paciente")

    modulo = Modulo()
    modulo.inicializar(test_path)

    window = QtWidgets.QMainWindow()
    window.setCentralWidget(modulo.get_workspace())

    dock = QtWidgets.QDockWidget("Ferramentas")
    tabs = QtWidgets.QTabWidget()
    for n, w in modulo.get_toolboxes().items():
        tabs.addTab(w, n)
    dock.setWidget(tabs)

    window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    window.show()
    sys.exit(app.exec())