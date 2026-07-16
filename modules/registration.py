import logging
import uuid
import vtk
from pathlib import Path
from typing import Optional, Dict

from PySide6 import QtWidgets, QtCore, QtGui

from core.scene.scene_object import SceneObject
from core.scene.scene_state import SceneState
from core.scene.scene_manager import SceneManager
from core.scene.events.event_bus import EventBus
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.selection.selection_manager import SelectionManager
from core.scene.persistence.serializer import Serializer
from core.scene.events.scene_events import SceneEvents, RegistrationEvents
from core.scene.io.importer import ObjectImporter

from core.workspace.contracts import IModule
from core.components.central_area.viewer_registration_central_area import ViewerRegistration_Widget_CentralArea
from core.components.side_panel.object_manager_sidepanel import ObjectManager_SidePanel
from core.components.side_panel.objetct_properties_sidepanel import ObjectProperties_SidePanel
from core.components.toolbars.registration_toolbar import RegistrationToolbar

logger = logging.getLogger("OpenCMF.RegistrationModule")


class Modulo(IModule):
    """Módulo de Registro/Alinhamento de objetos - Implementação da interface IModule"""

    def __init__(self, scene_manager: Optional[SceneManager] = None):
        super().__init__()

        self.nome = "Alinhar objetos"
        self.id = "modulo.registration"
        self.pasta_paciente = ""

        # Gerencia SceneManager (cria um padrão se não fornecido)
        self.scene_manager = scene_manager or self._criar_scene_manager_padrao()

        # Componentes internos
        self.serializer = Serializer()
        self.object_manager: Optional[ObjectImporter] = None
        self._toolbar: Optional[QtWidgets.QToolBar] = None
        self._toolbar_handler: Optional[RegistrationToolbar] = None
        self._is_initialized = False

        # UI Components
        self.widget_reg = ViewerRegistration_Widget_CentralArea(
            context=self.scene_manager,
            titulo="Registro"
        )

        self.widget_objetos = ObjectManager_SidePanel(
            context=self.scene_manager,
            titulo="Registro"
        )

        self.widget_propriedades = ObjectProperties_SidePanel(
            context=self.scene_manager,
            titulo="Propriedades"
        )

        # Cache para evitar múltiplas conexões
        self._subscribers = []

        # Conecta os sinais
        self._conectar_sinais()

    # ==================== Configuração Inicial ====================

    def _criar_scene_manager_padrao(self) -> SceneManager:
        """Cria um SceneManager com configuração padrão para o módulo."""
        bus = EventBus()
        state = SceneState()
        base_patient_path = "C:/OpenCMF/data/default_patient"
        importer = ObjectImporter(patient_path=base_patient_path)

        return SceneManager(
            state=state,
            event_bus=bus,
            object_registry=ObjectRegistry(),
            actor_registry=ActorRegistry(),
            selection_manager=SelectionManager(event_bus=bus, state=state),
            importer=importer
        )

    def _conectar_sinais(self):
        """Conecta os sinais do gerenciador de cena usando o sistema de eventos."""
        # Armazena referências para unsubscribe posterior
        self._subscribers = [
            (RegistrationEvents.ALIGNMENT_REQUESTED, self._executar_registro),
            (RegistrationEvents.CLEAR_POINTS, self._resetar_pontos),
            (RegistrationEvents.TARGET_CHANGED,
             lambda oid: self._carregar_na_vista_por_id(oid, "A")),
            (RegistrationEvents.SOURCE_CHANGED,
             lambda oid: self._carregar_na_vista_por_id(oid, "B")),
            (SceneEvents.INTERACTION_MODE_CHANGED, self._on_interaction_mode_changed),
            (SceneEvents.OBJECT_REMOVED, self._on_scene_object_removed),
            (SceneEvents.OBJECT_ADDED, self._on_scene_object_added),
        ]

        for event, callback in self._subscribers:
            self.scene_manager.events.subscribe(event, callback)

    # ==================== Handlers de Eventos ====================

    def _on_interaction_mode_changed(self, mode: str):
        """Handler para mudança de modo de interação."""
        if hasattr(self.widget_reg, "set_interaction_mode"):
            self.widget_reg.set_interaction_mode(mode)

    def _carregar_na_vista_por_id(self, oid: str, vista: str):
        """Carrega um objeto na vista especificada pelo ID."""
        obj = self.scene_manager.get_object(oid)
        if obj:
            self._carregar_na_vista(obj, vista)

    def _carregar_na_vista(self, obj: SceneObject, vista: str):
        """Carrega um objeto na vista especificada."""
        if not self.pasta_paciente:
            logger.error("Caminho do paciente não definido!")
            return

        if not obj.file_path:
            logger.warning(f"Objeto {obj.name} não possui caminho de arquivo definido.")
            return

        full_path = Path(self.pasta_paciente) / obj.file_path
        if not full_path.exists():
            logger.error(f"Arquivo não encontrado: {full_path}")
            return

        ext = full_path.suffix.lower()
        reader = self._criar_reader_por_extensao(ext)
        if reader is None:
            return

        try:
            reader.SetFileName(str(full_path))
            reader.Update()
            poly_data = reader.GetOutput()

            if not poly_data or poly_data.GetNumberOfPoints() == 0:
                logger.error(f"O arquivo {full_path} está vazio ou corrompido.")
                return

            # Adiciona à vista apropriada
            if vista == "A":
                self.widget_reg.adicionar_malha_vista_a(obj.name, poly_data, obj_id=obj.id)
            else:
                self.widget_reg.adicionar_malha_vista_b(obj.name, poly_data, obj_id=obj.id)

            logger.info(f"Objeto {obj.name} carregado com sucesso na Vista {vista}")

        except Exception as e:
            logger.error(f"Erro ao carregar objeto {obj.name} na vista {vista}: {e}")

    def _criar_reader_por_extensao(self, ext: str):
        """Cria o reader VTK apropriado para a extensão."""
        readers = {
            ".stl": vtk.vtkSTLReader,
            ".obj": vtk.vtkOBJReader,
            ".vti": vtk.vtkXMLImageDataReader,
            ".ply": vtk.vtkPLYReader,
            ".vtk": vtk.vtkPolyDataReader,
        }

        reader_class = readers.get(ext.lower())
        if reader_class:
            return reader_class()
        else:
            logger.warning(f"Formato não suportado automaticamente: {ext}")
            return None

    def _on_scene_object_added(self, obj: SceneObject):
        """Handler para quando um objeto é adicionado à cena."""
        # Verifica se o objeto já existe no registry
        if not self.scene_manager.objects.has(obj.id):
            self.scene_manager.add_object(obj)

        # Carrega nas vistas se o objeto tiver file_path
        if hasattr(obj, 'file_path') and obj.file_path:
            self._carregar_na_vista(obj, "A")
            self._carregar_na_vista(obj, "B")

        # Atualiza UI
        self.widget_objetos.adicionar_objeto_lista(
            obj.name,
            obj.type,
            QtGui.QColor.fromRgbF(*obj.color),
            objeto_id=obj.id
        )
        self._atualizar_ui_combos()

    def _atualizar_ui_combos(self):
        """Atualiza os combos da UI com a lista de objetos."""
        objs = [{"id": o.id, "name": o.name} for o in self.scene_manager.objects.all()]
        if hasattr(self.widget_reg, "atualizar_combos"):
            self.widget_reg.atualizar_combos(objs)

    def _on_visibility_toggled(self, oid: str, visible: bool):
        """Handler para toggle de visibilidade."""
        self.scene_manager.update_visibility(oid, visible)

    def _on_opacity_changed_ui(self, oid: str, opacity: float):
        """Handler para mudança de opacidade."""
        self.scene_manager.update_opacity(oid, opacity)

    def _on_color_changed_ui(self, oid: str, color: QtGui.QColor):
        """Handler para mudança de cor."""
        rgb = (color.redF(), color.greenF(), color.blueF())
        self.scene_manager.update_color(oid, rgb)

    def _on_import_request(self, **kwargs):
        """Handler para solicitação de importação de arquivo."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Importar Malha", "", "Malhas (*.stl *.obj *.ply)"
        )
        if path and self.object_manager:
            try:
                self.object_manager.import_external_file(
                    path,
                    kwargs.get("category", "models"),
                    uuid.uuid4().hex[:12]
                )
                logger.info(f"Arquivo importado com sucesso: {path}")
            except Exception as e:
                logger.error(f"Erro ao importar arquivo {path}: {e}")

    def _executar_registro(self):
        """Executa o processo de registro."""
        logger.info("Executando registro...")
        # TODO: Implementar lógica de registro

        # Emite evento de conclusão se necessário
        # self.scene_manager.events.emit(RegistrationEvents.ALIGNMENT_COMPLETED)

    def _resetar_pontos(self):
        """Reseta os pontos de referência."""
        if hasattr(self.widget_reg, "limpar_marcadores"):
            self.widget_reg.limpar_marcadores()
        if hasattr(self.widget_reg, "limpar_tabela"):
            self.widget_reg.limpar_tabela()
        logger.info("Pontos de referência resetados")

    def _on_scene_object_removed(self, object_id: str):
        """Handler para remoção de objeto da cena."""
        self.widget_objetos.remover_objeto_lista(object_id)

        # Remove da vista se o método existir
        if hasattr(self.widget_reg, "view_registration") and \
                hasattr(self.widget_reg.view_registration, "limpar_objeto"):
            self.widget_reg.view_registration.limpar_objeto(object_id)

        self._atualizar_ui_combos()
        logger.info(f"Objeto {object_id} removido da cena")

    # ==================== Implementação de IModule ====================

    def get_main_widget(self) -> QtWidgets.QWidget:
        """Retorna o widget principal do módulo."""
        return self.widget_reg

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        """
        Retorna a toolbar específica do módulo.
        Cria a toolbar e o handler na primeira chamada.
        """
        if self._toolbar is None:
            try:
                # Cria a toolbar
                self._toolbar = QtWidgets.QToolBar("Ferramentas de Registro")
                self._toolbar.setObjectName("registration_toolbar")

                # Cria o handler com o scene_manager
                self._toolbar_handler = RegistrationToolbar(
                    scene_manager=self.scene_manager
                )

                # Configura a toolbar baseado no que o handler suporta
                if hasattr(self._toolbar_handler, 'setup_toolbar'):
                    self._toolbar_handler.setup_toolbar(self._toolbar)
                elif hasattr(self._toolbar_handler, 'toolbar'):
                    # Se o handler já tem uma toolbar, usamos ela
                    self._toolbar = self._toolbar_handler.toolbar
                    self._toolbar.setObjectName("registration_toolbar")
                elif hasattr(self._toolbar_handler, 'create_actions'):
                    # Se o handler tem método create_actions
                    actions = self._toolbar_handler.create_actions()
                    for action in actions:
                        self._toolbar.addAction(action)
                else:
                    # Fallback: adicionar ações básicas manualmente
                    self._adicionar_acoes_basicas_toolbar()

                # Conecta evento de importação se não estiver conectado
                try:
                    self.scene_manager.events.subscribe(
                        RegistrationEvents.IMPORT_REQUESTED,
                        self._on_import_request
                    )
                except Exception as e:
                    logger.debug(f"Evento IMPORT_REQUESTED já conectado: {e}")

            except Exception as e:
                logger.error(f"Erro ao criar toolbar: {e}")
                # Fallback para toolbar básica
                self._toolbar = QtWidgets.QToolBar("Ferramentas de Registro")
                self._toolbar.setObjectName("registration_toolbar")
                self._adicionar_acoes_basicas_toolbar()

        return self._toolbar

    def _adicionar_acoes_basicas_toolbar(self):
        """Adiciona ações básicas à toolbar (fallback)."""
        if not self._toolbar:
            return

        # Ação de importar
        import_action = QtGui.QAction(QtGui.QIcon(), "Importar", self._toolbar)
        import_action.setToolTip("Importar malha")
        import_action.triggered.connect(lambda: self._on_import_request())
        self._toolbar.addAction(import_action)

        self._toolbar.addSeparator()

        # Ação de executar registro
        register_action = QtGui.QAction(QtGui.QIcon(), "Registrar", self._toolbar)
        register_action.setToolTip("Executar registro")
        register_action.triggered.connect(self._executar_registro)
        self._toolbar.addAction(register_action)

        # Ação de resetar pontos
        reset_action = QtGui.QAction(QtGui.QIcon(), "Resetar", self._toolbar)
        reset_action.setToolTip("Resetar pontos de referência")
        reset_action.triggered.connect(self._resetar_pontos)
        self._toolbar.addAction(reset_action)

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna os painéis laterais do módulo."""
        return {
            "Objetos": self.widget_objetos,
            "Propriedades": self.widget_propriedades
        }

    def cleanup(self) -> None:
        """Limpa os recursos do módulo."""
        if not self._is_initialized:
            return

        logger.info("Limpando recursos do módulo de Registro...")

        # Desconecta todos os subscribers
        for event, callback in self._subscribers:
            try:
                self.scene_manager.events.unsubscribe(event, callback)
            except Exception as e:
                logger.debug(f"Erro ao desconectar {event}: {e}")

        self._subscribers.clear()

        # Desconecta o import handler
        try:
            self.scene_manager.events.unsubscribe(
                RegistrationEvents.IMPORT_REQUESTED,
                self._on_import_request
            )
        except Exception as e:
            logger.debug(f"Erro ao desconectar import handler: {e}")

        # Desconecta o object_manager
        if hasattr(self, 'object_manager') and self.object_manager:
            try:
                self.object_manager.object_added.disconnect(self._on_scene_object_added)
            except Exception as e:
                logger.debug(f"Erro ao desconectar object_added: {e}")

        # Limpa UI components
        for widget in [self.widget_reg, self.widget_objetos, self.widget_propriedades]:
            if widget and hasattr(widget, 'cleanup'):
                try:
                    widget.cleanup()
                except Exception as e:
                    logger.debug(f"Erro ao limpar widget {widget.__class__.__name__}: {e}")

        # Limpa scene manager
        if self.scene_manager:
            try:
                self.scene_manager.clear()
            except Exception as e:
                logger.error(f"Erro ao limpar scene manager: {e}")

        # Limpa toolbar
        if self._toolbar:
            self._toolbar.clear()
            self._toolbar = None
            self._toolbar_handler = None

        self._is_initialized = False
        logger.info("Limpeza concluída")

    # ==================== Métodos Públicos Adicionais ====================

    def inicializar(self, caminho_paciente: str) -> None:
        """
        Inicializa o módulo com o caminho do paciente.
        Este método deve ser chamado após a instanciação.
        """
        if self._is_initialized:
            logger.warning("Módulo já inicializado. Reinicializando...")
            self.cleanup()

        self.pasta_paciente = caminho_paciente

        # Cria o object manager com o caminho do paciente
        self.object_manager = ObjectImporter(patient_path=caminho_paciente)
        self.object_manager.object_added.connect(self._on_scene_object_added)

        # Atualiza estado do scene manager
        self.scene_manager.state.current_patient = caminho_paciente

        # Passa o caminho para os widgets
        if hasattr(self.widget_objetos, "set_patient_path"):
            self.widget_objetos.set_patient_path(caminho_paciente)

        # Conecta o properties panel à view de registro
        if hasattr(self.widget_reg, "view_registration") and \
                hasattr(self.widget_reg.view_registration, "connect_properties_panel"):
            self.widget_reg.view_registration.connect_properties_panel(self.widget_propriedades)

        # Carrega dados do paciente se disponível
        if hasattr(self.object_manager, "load_patient_data"):
            try:
                self.object_manager.load_patient_data()
                logger.info("Dados do paciente carregados com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar dados do paciente: {e}")

        self._is_initialized = True
        logger.info(f"Módulo de Registro inicializado com paciente: {caminho_paciente}")


# ==================== Bloco de Teste ====================

if __name__ == "__main__":
    import sys
    import os

    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Setup de ambiente de teste
    test_path = os.path.abspath("./teste_paciente")
    os.makedirs(test_path, exist_ok=True)

    # Cria arquivos de teste
    test_file = os.path.join(test_path, "test.stl")
    if not os.path.exists(test_file):
        with open(test_file, 'w') as f:
            f.write("solid test\nendsolid test\n")

    # Instanciação do módulo
    modulo = Modulo()
    modulo.inicializar(test_path)

    # Container de teste
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Teste Isolado - Módulo de Registro")
    window.resize(1200, 800)

    # Central Widget
    window.setCentralWidget(modulo.get_main_widget())

    # Toolbar
    toolbar = modulo.get_workspace_toolbar()
    if toolbar:
        window.addToolBar(toolbar)

    # Painéis Laterais
    dock = QtWidgets.QDockWidget("Painel de Controle")
    dock.setObjectName("painel_controle")
    tabs = QtWidgets.QTabWidget()
    for titulo, widget in modulo.get_toolboxes().items():
        tabs.addTab(widget, titulo)
    dock.setWidget(tabs)
    window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    window.show()
    sys.exit(app.exec())