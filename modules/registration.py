import vtk
import sys
import os
import random
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from core.base_module.base import ModuloBase
from core.components.central_area.window_registration import WindowRegistration
from core.components.toolboxes.object_manager_toolbox import ObjetoManagerWidget
from core.components.toolboxes.registration_toolbox import RegistrationWidget

from core.imports.object_manager import ObjectManager
from core.imports.models_import import ObjectProperties


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Registro"
        self.id = "modulo.registration"
        self.view_registro: Optional[WindowRegistration] = None
        self.widget_reg = RegistrationWidget()
        self.widget_objetos = ObjetoManagerWidget()
        self.manager: Optional[ObjectManager] = None
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
        self.manager = ObjectManager(caminho_paciente)
        self.manager.object_added.connect(self._on_object_added_manager)

        if not self.view_registro:
            self.view_registro = WindowRegistration()

        handler = self.view_registro.toolbar_handler
        if handler:
            # O sinal agora passa os nomes da categoria e subcategoria do painel UI
            handler.importRequested.connect(self._handle_import)
            handler.deletePointRequested.connect(self.view_registro.remover_ultimo_ponto)
            handler.pointSizeChanged.connect(self._on_point_size_changed)

        self.view_registro.pontoAdicionado.connect(self._on_ponto_adicionado_na_janela)

        # Carrega objetos que já possuem JSON na pasta do paciente
        self.manager.load_existing_objects()

    def _handle_import(self, categoria: str, sub_categoria: str):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, f"Importar {sub_categoria}", "", "Malhas (*.stl *.obj *.ply);;Todos (*.*)"
        )
        if file_path:
            self.manager.import_object(file_path, categoria, sub_categoria)

    def _on_object_added_manager(self, props: ObjectProperties):
        # Atualiza a UI da toolbox com base nas propriedades do novo objeto
        self.widget_objetos.adicionar_objeto_lista(
            props.name,
            props.type.capitalize(),
            cor=props.render["color"]
        )

        # Atualiza os combos de seleção para o registro
        nomes = [obj.name for obj in self.manager.objects.values()]
        if hasattr(self.widget_reg, 'atualizar_combos'):
            self.widget_reg.atualizar_combos(nomes)

    def _on_objeto_toggled(self, nome, visivel):
        if not self.view_registro or not self.manager:
            return

        if visivel:
            # Busca o objeto no manager pelo nome (sub_categoria)
            props = next((p for p in self.manager.objects.values() if p.name == nome), None)
            if props:
                full_path = self.manager.patient_path / props.file_path
                polydata = self._carregar_polydata(full_path)

                if polydata:
                    target_name = self.widget_reg.get_target_name()
                    if nome == target_name:
                        self.view_registro.adicionar_malha_vista_a(nome, polydata)
                    else:
                        self.view_registro.adicionar_malha_vista_b(nome, polydata)
        else:
            self.view_registro.remover_objeto(nome)

    def _carregar_polydata(self, path: Path):
        ext = path.suffix.lower()
        if ext == ".stl":
            reader = vtk.vtkSTLReader()
        elif ext == ".obj":
            reader = vtk.vtkOBJReader()
        elif ext == ".ply":
            reader = vtk.vtkPLYReader()
        else:
            return None

        reader.SetFileName(str(path))
        reader.Update()
        return reader.GetOutput()

    def _on_delete_requested(self, nome):
        props = next((p for p in self.manager.objects.values() if p.name == nome), None)
        if props:
            self.manager.remove_object(props.id)
            if self.view_registro:
                self.view_registro.remover_objeto(nome)