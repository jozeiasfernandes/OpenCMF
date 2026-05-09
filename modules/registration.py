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
from core.components.toolbars.registration_toolbar import Component as RegistrationToolbar
from core.imports.object_manager import ObjectManager

# Desativar erros chatos do VTK no console, a menos que seja estritamente necessário
os.environ["VTK_SILENT_ERRORS"] = "1"
vtk.vtkObject.GlobalWarningDisplayOff()

logger = logging.getLogger("RegistrationModule")


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Alinhar objetos"
        self.id = "modulo.registration"
        self.pasta_paciente = None
        self.object_manager: Optional[ObjectManager] = None

        # Componentes de UI
        self.view_registration = WindowRegistration()
        self.widget_reg = Component()
        self.widget_objetos = ObjetoManagerWidget()

        self._conectar_sinais()

    def _conectar_sinais(self):
        # --- Sinais da Toolbox de Registro (Lateral) ---
        self.widget_reg.solicitarAlinhamento.connect(self._executar_registro)
        self.widget_reg.limparPontos.connect(self._resetar_pontos)
        self.widget_reg.targetChanged.connect(self._on_target_combo_changed)
        self.widget_reg.sourceChanged.connect(self._on_source_combo_changed)

        # --- Sinais da Área Central (View 3D) ---
        # Sincroniza combos centrais com a lógica do módulo
        self.view_registration.requisitarCarregamentoObjeto.connect(self._on_requisicao_central_carregamento)
        self.view_registration.pontoAdicionado.connect(self.widget_reg.adicionar_ponto_tabela)

        # --- Sinais da Toolbox de Objetos (Gerenciador) ---
        self.widget_objetos.objetoToggled.connect(self._on_objeto_toggled)
        self.widget_objetos.opacityChanged.connect(self._on_opacity_changed)
        self.widget_objetos.colorChanged.connect(self._on_color_changed)
        self.widget_objetos.deleteRequested.connect(self._on_delete_requested)
        self.widget_objetos.nomeAlterado.connect(self._on_nome_alterado)

    def inicializar(self, caminho_paciente: str) -> None:
        novo_path = str(Path(caminho_paciente).resolve())
        if self.pasta_paciente == novo_path:
            return

        super().inicializar(novo_path)
        self.pasta_paciente = novo_path
        logger.info(f"Módulo Registro inicializado para: {novo_path}")

        # Inicializa o gerenciador de arquivos do paciente
        self.object_manager = ObjectManager(novo_path)
        self.object_manager.object_added.connect(self._on_object_added_manager)
        self.object_manager.load_existing_objects()

    # --- SINCRONIZAÇÃO E CARREGAMENTO ---

    def _on_requisicao_central_carregamento(self, vista_id, nome):
        """
        Sincroniza a mudança feita nos combos da área central com a toolbox lateral
        e carrega a malha.
        """
        if vista_id == "A":
            # Atualiza o combo da lateral silenciosamente para evitar loops
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
        if not nome: return
        props = next((p for p in self.object_manager.objects.values() if p.name == nome), None)
        if props:
            self._carregar_na_vista(props, "A")

    def _on_source_combo_changed(self, nome: str):
        if not nome: return
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

    def _on_object_added_manager(self, props):
        """Chamado quando um novo objeto é importado ou carregado do disco."""
        categoria = self._mapear_categoria_para_tipo(props.type)
        self.widget_objetos.adicionar_objeto_lista(
            props.name, categoria, props.render["color"], objeto_id=props.id
        )

        # Atualiza as listas de seleção em todos os lugares
        nomes_objetos = [obj.name for obj in self.object_manager.objects.values()]
        self.widget_reg.atualizar_combos(nomes_objetos)
        self.view_registration.atualizar_lista_objetos(nomes_objetos)

    def _on_objeto_toggled(self, nome, visivel):
        """Trata a visibilidade vinda da toolbox de objetos."""
        if not visivel:
            self.view_registration.remover_objeto(nome)
        else:
            # Se o objeto foi ligado, verifica se ele é o selecionado nos combos de alinhamento
            if nome == self.widget_reg.get_target_name():
                self._on_target_combo_changed(nome)
            elif nome == self.widget_reg.get_source_name():
                self._on_source_combo_changed(nome)

    def _on_opacity_changed(self, nome, valor):
        """Repassa a opacidade da toolbox para a área 3D."""
        self.view_registration.set_objeto_opacidade(nome, valor)

    def _on_color_changed(self, nome, color):
        """Repassa a cor da toolbox para a área 3D."""
        # Converte QColor para tuple RGB (0.0 a 1.0)
        rgb = (color.redF(), color.greenF(), color.blueF())
        self.view_registration.set_objeto_cor(nome, rgb)

    # --- INTERFACE E OPERAÇÕES ---

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        toolbar = RegistrationToolbar()
        h = toolbar.handler
        h.importRequested.connect(lambda: self._importar_objeto("surfaces", "Importado"))
        h.deletePointRequested.connect(self.view_registration.remover_ultimo_marcador)
        h.pointSizeChanged.connect(self.view_registration.set_ponto_raio)
        h.resetLayoutRequested.connect(self.view_registration.reset_layout_vistas)
        return toolbar

    def get_workspace(self) -> QtWidgets.QWidget:
        return self.view_registration

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {"Alinhar Objetos": self.widget_reg, "Objetos": self.widget_objetos}

    def _executar_registro(self):
        pts_a = self.view_registration.get_points_a()
        pts_b = self.view_registration.get_points_b()
        if len(pts_a) < 3 or len(pts_a) != len(pts_b):
            QtWidgets.QMessageBox.warning(self.view_registration, "Aviso",
                                          "Marque pelo menos 3 pontos correspondentes em cada vista.")
            return

        logger.info(f"Iniciando registro com {len(pts_a)} pontos.")
        # Lógica de Landmark Transform viria aqui...

    def _resetar_pontos(self):
        self.view_registration.limpar_marcadores()
        self.widget_reg.limpar_tabela()

    def _importar_objeto(self, categoria: str, subcategoria: str) -> None:
        if not self.object_manager: return
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.view_registration, "Importar STL", "", "STL (*.stl)"
        )
        if path:
            # O ObjectManager cuida de copiar o arquivo e emitir o sinal object_added
            self.object_manager.import_object(path, categoria, subcategoria)

    def _mapear_categoria_para_tipo(self, tipo_pasta: str) -> str:
        mapeamento = {
            "surfaces": "Superfícies",
            "photos": "Fotografias",
            "volume": "Volume",
            "implants": "Implantes"
        }
        return mapeamento.get(tipo_pasta, "Outros")

    def _on_delete_requested(self, nome):
        # Aqui você deve decidir se deleta do disco via ObjectManager ou só da view
        self.view_registration.remover_objeto(nome)
        # self.object_manager.delete_object(nome) # Se quiser deletar o arquivo

    def _on_nome_alterado(self, nome_original: str, novo_nome: str) -> None:
        # Atualiza no dicionário de dados e propaga para os combos
        for props in self.object_manager.objects.values():
            if props.name == nome_original:
                props.name = novo_nome
                break

        nomes = [obj.name for obj in self.object_manager.objects.values()]
        self.widget_reg.atualizar_combos(nomes)
        self.view_registration.atualizar_lista_objetos(nomes)


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