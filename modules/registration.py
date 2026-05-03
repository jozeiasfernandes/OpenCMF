import vtk
import sys
import os
import random
import logging
import traceback
from typing import Optional, Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.base_module.base import ModuloBase
from core.components.central_area.window_registration import WindowRegistration
from core.components.toolboxes.object_manager_toolbox import ObjetoManagerWidget
from core.components.toolboxes.registration_toolbox import RegistrationWidget
from core.imports.import_objets import FileImporter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("RegistrationModule")

os.environ["VTK_SILENT_ERRORS"] = "1"
vtk.vtkObject.GlobalWarningDisplayOff()


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        logger.debug("Inicializando Modulo Registration")
        self.nome = "Alinhar objetos"
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
        try:
            logger.info(f"Inicializando com paciente: {caminho_paciente}")
            super().inicializar(caminho_paciente)

            if not self.view_registro:
                logger.debug("Criando WindowRegistration")
                self.view_registro = WindowRegistration()

            self._setup_toolbar_handlers()
            self.view_registro.pontoAdicionado.connect(self._on_ponto_adicionado_na_janela)
            self._atualizar_lista_objects()

        except Exception as e:
            logger.error(f"Falha na inicialização do módulo: {e}")
            logger.error(traceback.format_exc())

    def _setup_toolbar_handlers(self):
        if not self.view_registro:
            return

        handler = getattr(self.view_registro, 'toolbar_handler', None)
        if handler:
            logger.debug("Conectando handlers da toolbar")
            handler.importRequested.connect(self._handle_import)
            handler.deletePointRequested.connect(self.view_registro.remover_ultimo_ponto)
            handler.pointSizeChanged.connect(self._on_point_size_changed)
            if hasattr(handler, 'resetLayoutRequested'):
                handler.resetLayoutRequested.connect(self.view_registro.reset_layout_vistas)

    def _on_point_size_changed(self, size: float):
        if not self.view_registro: return
        try:
            for view in [self.view_registro.view_a, self.view_registro.view_b]:
                if not view or not view.renderer: continue
                actors = view.renderer.GetActors()
                actors.InitTraversal()
                for _ in range(actors.GetNumberOfItems()):
                    actor = actors.GetNextActor()
                    mapper = actor.GetMapper()
                    if mapper and (source := mapper.GetInputAlgorithm()):
                        if isinstance(source, vtk.vtkSphereSource):
                            source.SetRadius(size)
                view.render()
        except Exception as e:
            logger.error(f"Erro ao mudar tamanho do ponto: {e}")

    def _on_ponto_adicionado_na_janela(self, vista, pos):
        if hasattr(self.widget_reg, 'adicionar_ponto_tabela'):
            self.widget_reg.adicionar_ponto_tabela(vista, pos)

    def _handle_import(self):
        if FileImporter.import_files_to_patient(self.pasta_paciente):
            self._atualizar_lista_objects()

    def _atualizar_lista_objects(self):
        if not self.widget_objetos or not self.pasta_paciente: return
        try:
            path_stl = Path(self.pasta_paciente) / "STL"
            path_stl.mkdir(parents=True, exist_ok=True)
            self.widget_objetos.tree_widget.clear()
            self.widget_objetos.cats.clear()

            arquivos = sorted(path_stl.glob("*.stl"))
            nomes = [f.name for f in arquivos]

            for nome in nomes:
                cor = [random.random() for _ in range(3)]
                self.widget_objetos.adicionar_objeto_lista(nome, "Superfícies", cor=cor)

            if hasattr(self.widget_reg, 'atualizar_combos'):
                self.widget_reg.atualizar_combos(nomes)
        except Exception as e:
            logger.error(f"Erro ao atualizar lista: {e}")

    def _on_objeto_toggled(self, nome, visivel):
        if not self.view_registro: return
        try:
            if visivel:
                path = Path(self.pasta_paciente) / "STL" / nome
                if path.exists():
                    logger.debug(f"Carregando malha: {nome}")
                    reader = vtk.vtkSTLReader()
                    reader.SetFileName(str(path))
                    reader.Update()

                    target = self.widget_reg.get_target_name()
                    if nome == target:
                        self.view_registro.adicionar_malha_vista_a(nome, reader.GetOutput())
                    else:
                        self.view_registro.adicionar_malha_vista_b(nome, reader.GetOutput())
            else:
                self.view_registro.remover_objeto(nome)
        except Exception as e:
            logger.error(f"Erro ao alternar objeto {nome}: {e}")

    def _on_opacity_changed(self, nome, valor):
        if self.view_registro: self.view_registro.set_objeto_opacidade(nome, valor)

    def _on_color_changed(self, nome, color):
        if self.view_registro:
            rgb = (color.redF(), color.greenF(), color.blueF())
            self.view_registro.set_objeto_cor(nome, rgb)

    def _on_delete_requested(self, nome):
        try:
            if self.view_registro: self.view_registro.remover_objeto(nome)
            path = Path(self.pasta_paciente) / "STL" / nome
            if path.exists(): os.remove(path)
            self._atualizar_lista_objects()
        except Exception as e:
            logger.error(f"Erro ao deletar {nome}: {e}")

    def _executar_registro_landmarking(self):
        if not self.view_registro: return
        pa, pb = self.view_registro.get_points_a(), self.view_registro.get_points_b()
        if len(pa) < 3 or len(pa) != len(pb):
            QtWidgets.QMessageBox.warning(None, "Erro", "Pontos insuficientes ou incompatíveis.")
            return
        logger.info(f"Registro iniciado com {len(pa)} pontos.")

    def _resetar_pontos(self):
        if self.view_registro: self.view_registro.limpar_marcadores()
        self.widget_reg.limpar_tabela()

    def get_workspace(self) -> QtWidgets.QWidget:
        if not self.view_registro:
            logger.debug("Criando view_registro via get_workspace")
            self.view_registro = WindowRegistration()

        # Garante que o VTK só inicialize interatores quando solicitado pela UI
        QtCore.QTimer.singleShot(500, self._safe_interactor_setup)
        return self.view_registro

    def _safe_interactor_setup(self):
        if self.view_registro and hasattr(self.view_registro, 'setup_interactors'):
            try:
                logger.debug("Iniciando setup_interactors VTK")
                self.view_registro.setup_interactors()
            except Exception as e:
                logger.error(f"Crash no setup_interactors VTK: {e}")

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {"Configuração": self.widget_reg, "Arquivos": self.widget_objetos}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    test_path = os.path.abspath("./teste_registro")
    os.makedirs(os.path.join(test_path, "STL"), exist_ok=True)

    modulo = Modulo()
    modulo.inicializar(test_path)

    window = QtWidgets.QMainWindow()
    window.setCentralWidget(modulo.get_workspace())
    window.show()
    sys.exit(app.exec())