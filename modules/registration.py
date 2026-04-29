import vtk
import sys
import os
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore

root_path = str(Path(__file__).parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from core.base_module.base import ModuloBase
from core.components.windows.window_registration.window_registration import WindowRegistration
from core.components.toolboxes.object_manager_widget import ObjetoManagerWidget
from core.components.toolboxes.registration_widget import RegistrationWidget
from core.imports.import_objets import FileImporter


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
        self.widget_objetos.requestRefresh.connect(self._atualizar_lista_objects)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        if not self.view_registro:
            self.view_registro = WindowRegistration()

        try:
            if hasattr(self.view_registro, 'toolbar_handler') and self.view_registro.toolbar_handler:
                self.view_registro.toolbar_handler.importRequested.connect(self._handle_import)
        except AttributeError:
            print("Aviso: Toolbar handler não encontrado na inicialização.")

        self._atualizar_lista_objects()

    def _handle_import(self):
        if FileImporter.import_files_to_patient(self.pasta_paciente):
            self._atualizar_lista_objects()

    def _atualizar_lista_objects(self):
        if self.widget_objetos and self.pasta_paciente:
            pasta_stl = Path(self.pasta_paciente) / "STL"
            pasta_stl.mkdir(parents=True, exist_ok=True)

            self.widget_objetos.atualizar_lista(pasta_stl=str(pasta_stl))
            nomes_objetos = [f.name for f in sorted(pasta_stl.glob("*.stl"))]
            self.widget_reg.atualizar_combos(nomes_objetos)

    def _on_objeto_toggled(self, nome, visivel):
        if not self.view_registro:
            return

        if visivel:
            if nome == "volume DICOM":
                self.view_registro.view_a.toggle_volume_visibility(True)
                self.view_registro.view_b.toggle_volume_visibility(True)
            else:
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
            if nome == "volume DICOM":
                self.view_registro.view_a.toggle_volume_visibility(False)
                self.view_registro.view_b.toggle_volume_visibility(False)
            else:
                self.view_registro.remover_objeto(nome)

    def _executar_registro_landmarking(self):
        if not self.view_registro:
            return
        pontos_a = self.view_registro.get_points_a()
        pontos_b = self.view_registro.get_points_b()
        if len(pontos_a) < 3 or len(pontos_a) != len(pontos_b):
            QtWidgets.QMessageBox.warning(
                None, "Erro de Pontos",
                "Marque o mesmo número de pontos (mínimo 3) em ambas as vistas."
            )
            return
        print(f"Iniciando registro com {len(pontos_a)} pontos...")

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

    test_patient_path = os.path.abspath("./teste_registro_standalone")
    os.makedirs(os.path.join(test_patient_path, "STL"), exist_ok=True)

    modulo = Modulo()
    modulo.inicializar(test_patient_path)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle(f"Standalone - {modulo.nome}")
    window.resize(1280, 720)

    workspace = modulo.get_workspace()
    window.setCentralWidget(workspace)

    if hasattr(workspace, "toolbar"):
        window.addToolBar(workspace.toolbar)
    elif hasattr(workspace, "toolbar_handler"):
        window.addToolBar(workspace.toolbar_handler.toolbar)

    toolboxes = modulo.get_toolboxes()
    dock = QtWidgets.QDockWidget("Ferramentas", window)
    tab_widget = QtWidgets.QTabWidget()

    for nome, widget in toolboxes.items():
        tab_widget.addTab(widget, nome)

    dock.setWidget(tab_widget)
    window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    window.show()
    sys.exit(app.exec())