from typing import Tuple, Optional, Dict, Any, List
from PySide6 import QtWidgets, QtCore
from settings.logs.archives.module_log import Module_Logger
from core.workspace.models.contracts import IModule

# Scene
from core.application.scene.events.event_bus import EventBus


class ModuloBase(QtWidgets.QWidget):
    """Classe base para módulos que atuam como containers de componentes."""

    id: str = "undefined.id"
    nome: str = "Módulo Genérico"
    concluido = QtCore.Signal()

    def __init__(self, context: Any, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self.context = context
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        # --- GESTÃO AUTOMÁTICA DO EVENT BUS ---
        self._setup_event_bus()
        # -------------------------------------

        self.viewer: Optional[QtWidgets.QWidget] = None
        self.module_logger = Module_Logger(modulo_instance=self)

    def _setup_event_bus(self):
        """Garante que tanto o módulo quanto o contexto possuem um EventBus funcional."""
        bus = None

        # 1. Tenta obter do contexto existente
        if self.context and hasattr(self.context, "event_bus"):
            bus = self.context.event_bus

        # 2. Se não houver no contexto, tenta pegar da instância global da aplicação Qt
        if not bus:
            app_instance = QtWidgets.QApplication.instance()
            if app_instance and hasattr(app_instance, "event_bus"):
                bus = app_instance.event_bus

        # 3. Se ainda não existir em lugar nenhum, cria um novo EventBus local/compartilhado
        if not bus:
            bus = EventBus()

        # Atribui formalmente ao módulo e injeta no contexto para as ferramentas filhas
        self.event_bus = bus
        if self.context and hasattr(self.context, "__dict__"):
            setattr(self.context, "event_bus", self.event_bus)

    def get_central_area(self) -> QtWidgets.QWidget:
        """Retorna o widget principal da área central do módulo."""
        return self.viewer if self.viewer is not None else self

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna o dicionário de painéis laterais (side_panel)."""
        return {}

    def get_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        """Retorna a barra de ferramentas do módulo."""
        return None

    def get_bottom_panel(self) -> Optional[QtWidgets.QWidget]:
        """Retorna o painel inferior do módulo."""
        return None

    def inicializar(self, caminho_paciente: str) -> None:
        """Chamado pela orquestração do sistema."""
        self.configure_resources(caminho_paciente)
        self.module_logger.log_full_state()

    def cleanup(self) -> None:
        """Deve ser sobrescrito para limpar referências de componentes filhos."""
        pass

    def configure_resources(self, caminho_paciente: str) -> None:
        """Deve ser implementado pelas subclasses."""
        pass

    def verificar_pre_requisitos(self) -> Tuple[bool, str]:
        return True, ""

    def validar_passagem(self) -> bool:
        return True


# Registra formalmente a ModuloBase como uma subclasse virtual de IModule
IModule.register(ModuloBase)