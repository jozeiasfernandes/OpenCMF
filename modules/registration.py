import vtk
import sys
import os
import random
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.base_module.base import ModuloBase
from core.components.windows.window_registration import WindowRegistration
from core.components.toolboxes.object_manager_toolbox import ObjetoManagerWidget
from core.components.toolboxes.registration_toolbox import RegistrationWidget
from core.imports.import_objets import FileImporter

os.environ["VTK_SILENT_ERRORS"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

vtk.vtkObject.GlobalWarningDisplayOff()

class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Registro"
        self.id = "modulo.registration"
        self.view_registro: Optional[WindowRegistration] = None
        self.widget_reg = RegistrationWidget()
        self.widget_objetos = ObjetoManagerWidget()
        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_reg.solicitarAlinhamento.connect(self._executar_registro_landmarking)
        self.widget_reg.limparPontos.connect(self._resetar_pontos)
        self.widget_objetos.objetoToggled.connect(self._on_objeto_toggled)
        self.widget_objetos.opacityChanged.connect(self._on_opacity_changed)
        self.widget_objetos.colorChanged.connect(self._on_color_changed)
        self.widget_objetos.deleteRequested.connect(self._on_delete_requested)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        if not self.view_registro:
            self.view_registro = WindowRegistration()

        handler = self.view_registro.toolbar_handler
        if handler:
            handler.importRequested.connect(self._handle_import)
            handler.deletePointRequested.connect(self.view_registro.remover_ultimo_ponto)
            handler.pointSizeChanged.connect(self._on_point_size_changed)
            if hasattr(handler, 'resetLayoutRequested'):
                handler.resetLayoutRequested.connect(self.view_registro.reset_layout_vistas)

        self.view_registro.pontoAdicionado.connect(self._on_ponto_adicionado_na_janela)
        self._atualizar_lista_objects()

    def _on_point_size_changed(self, size: float):
        if not self.view_registro:
            return
        for view in [self.view_registro.view_a, self.view_registro.view_b]:
            actors = view.renderer.GetActors()
            actors.InitTraversal()
            for _ in range(actors.GetNumberOfItems()):
                actor = actors.GetNextActor()
                mapper = actor.GetMapper()
                if mapper:
                    source = mapper.GetInputAlgorithm()
                    if isinstance(source, vtk.vtkSphereSource):
                        source.SetRadius(size)
            view.render()

    def _on_ponto_adicionado_na_janela(self, vista, pos):
        if hasattr(self.widget_reg, 'adicionar_ponto_tabela'):
            self.widget_reg.adicionar_ponto_tabela(vista, pos)

    def _handle_import(self):
        if FileImporter.import_files_to_patient(self.pasta_paciente):
            self._atualizar_lista_objects()

    def _atualizar_lista_objects(self):
        if not self.widget_objetos or not self.pasta_paciente:
            return
        pasta_stl = Path(self.pasta_paciente) / "STL"
        pasta_stl.mkdir(parents=True, exist_ok=True)
        self.widget_objetos.tree_widget.clear()
        self.widget_objetos.cats.clear()
        arquivos = sorted(pasta_stl.glob("*.stl"))
        nomes_objetos = []
        for file_path in arquivos:
            nome = file_path.name
            nomes_objetos.append(nome)
            cor_padrao = [random.random() for _ in range(3)]
            self.widget_objetos.adicionar_objeto_lista(nome, "Superfícies", cor=cor_padrao)
        if hasattr(self.widget_reg, 'atualizar_combos'):
            self.widget_reg.atualizar_combos(nomes_objetos)

    def _on_objeto_toggled(self, nome, visivel):
        if not self.view_registro:
            return
        if visivel:
            path = Path(self.pasta_paciente) / "STL" / nome
            if path.exists():
                reader = vtk.vtkSTLReader()
                reader.SetFileName(str(path))
                reader.Update()
                polydata = reader.GetOutput()
                target_name = self.widget_reg.get_target_name()
                if nome == target_name:
                    self.view_registro.adicionar_malha_vista_a(nome, polydata)
                else:
                    self.view_registro.adicionar_malha_vista_b(nome, polydata)
        else:
            self.view_registro.remover_objeto(nome)

    def _on_opacity_changed(self, nome, valor):
        if self.view_registro:
            self.view_registro.set_objeto_opacidade(nome, valor)

    def _on_color_changed(self, nome, color):
        if self.view_registro:
            rgb = (color.redF(), color.greenF(), color.blueF())
            self.view_registro.set_objeto_cor(nome, rgb)

    def _on_delete_requested(self, nome):
        if self.view_registro:
            self.view_registro.remover_objeto(nome)
        path = Path(self.pasta_paciente) / "STL" / nome
        if path.exists():
            try:
                os.remove(path)
            except Exception as e:
                print(f"Erro: {e}")
        self._atualizar_lista_objects()

    def _executar_registro_landmarking(self):
        if not self.view_registro:
            return
        pa = self.view_registro.get_points_a()
        pb = self.view_registro.get_points_b()
        if len(pa) < 3 or len(pa) != len(pb):
            QtWidgets.QMessageBox.warning(None, "Erro", "Número de pontos inválido (mínimo 3 e iguais).")
            return
        print(f"Registro iniciado: {len(pa)} pontos.")

    def _resetar_pontos(self):
        if self.view_registro:
            self.view_registro.limpar_marcadores()
        self.widget_reg.limpar_tabela()

    def get_workspace(self) -> QtWidgets.QWidget:
        if not self.view_registro:
            self.view_registro = WindowRegistration()
            QtCore.QTimer.singleShot(500, self.view_registro.setup_interactors)
        return self.view_registro

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Configuração": self.widget_reg,
            "Arquivos": self.widget_objetos
        }

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    test_path = os.path.abspath("./teste_registro_standalone")
    os.makedirs(os.path.join(test_path, "STL"), exist_ok=True)
    modulo = Modulo()
    modulo.inicializar(test_path)
    window = QtWidgets.QMainWindow()
    window.setWindowTitle(f"Standalone - {modulo.nome}")
    window.resize(1280, 720)
    window.setCentralWidget(modulo.get_workspace())
    handler = modulo.view_registro.toolbar_handler
    if handler:
        window.addToolBar(handler.toolbar)
    toolboxes = modulo.get_toolboxes()
    dock = QtWidgets.QDockWidget("Painel", window)
    tabs = QtWidgets.QTabWidget()
    for n, w in toolboxes.items():
        tabs.addTab(w, n)
    dock.setWidget(tabs)
    window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    window.show()
    sys.exit(app.exec())