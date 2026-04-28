import vtk
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore

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
            self.widget_objetos.atualizar_lista(pasta_stl=str(pasta_stl))

            if pasta_stl.exists():
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