import vtk
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets

from core.base_module.base import ModuloBase
from core.windows.window_registration.window_registration import WindowRegistration
from core.toolboxes.object_manager_widget import ObjetoManagerWidget
from core.toolboxes.registration_widget import RegistrationWidget


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
        self._atualizar_lista_objects()

    def _atualizar_lista_objects(self):
        if self.widget_objetos and self.pasta_paciente:
            pasta_stl = Path(self.pasta_paciente) / "STL"
            self.widget_objetos.atualizar_lista(pasta_stl=str(pasta_stl))

            nomes_objetos = [Path(f).name for f in pasta_stl.glob("*.stl")]
            self.widget_reg.atualizar_combos(nomes_objetos)

    def _on_objeto_toggled(self, nome, visivel):
        if not self.view_registro: return

        target_name = self.widget_reg.get_target_name()
        source_name = self.widget_reg.get_source_name()

        if visivel:
            path = Path(self.pasta_paciente) / "STL" / nome
            if path.exists():
                reader = vtk.vtkSTLReader()
                reader.SetFileName(str(path))
                reader.Update()
                polydata = reader.GetOutput()

                if nome == target_name:
                    self.view_registro.adicionar_malha_vista_a(nome, polydata)
                elif nome == source_name:
                    self.view_registro.adicionar_malha_vista_b(nome, polydata)
                else:
                    self.view_registro.adicionar_malha_vista_a(nome, polydata)
        else:
            self.view_registro.remover_objeto(nome)

    def _executar_registro_landmarking(self):
        pontos_a = self.view_registro.get_points_a()
        pontos_b = self.view_registro.get_points_b()

        if len(pontos_a) < 3 or len(pontos_a) != len(pontos_b):
            QtWidgets.QMessageBox.warning(None, "Erro", "Marque o mesmo número de pontos em ambas as vistas.")
            return

        print(f"Alinhando {len(pontos_a)} pares de pontos...")

    def _resetar_pontos(self):
        if self.view_registro:
            self.view_registro.limpar_marcadores()
        self.widget_reg.limpar_tabela()

    def get_workspace(self) -> QtWidgets.QWidget:
        if not self.view_registro:
            self.view_registro = WindowRegistration()
        return self.view_registro

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Configuração": self.widget_reg,
            "Arquivos": self.widget_objetos
        }