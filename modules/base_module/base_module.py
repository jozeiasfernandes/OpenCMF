from typing import Tuple, Optional, Dict, Any, List
from PySide6 import QtWidgets, QtCore
from settings.logs.archives.module_log import Module_Logger
from core.workspace.models.contracts import IModule


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

        self.viewer: Optional[QtWidgets.QWidget] = None

        self.module_logger = Module_Logger(modulo_instance=self)

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
        self.configurar_recursos(caminho_paciente)
        self.module_logger.log_full_state()

    def cleanup(self) -> None:
        """Deve ser sobrescrito para limpar referências de componentes filhos."""
        pass

    def configurar_recursos(self, caminho_paciente: str) -> None:
        """Deve ser implementado pelas subclasses."""
        pass

    def verificar_pre_requisitos(self) -> Tuple[bool, str]:
        return True, ""

    def validar_passagem(self) -> bool:
        return True


# Registra formalmente a ModuloBase como uma subclasse virtual de IModule
# Isso faz com que isinstance(instance, IModule) retorne True sem causar conflito de metaclasse.
IModule.register(ModuloBase)


class FluxoBase:
    """Classe base para definição e controle de fluxos."""

    def __init__(self, dados: Dict[str, Any]):
        self.nome: str = dados.get("nome", "Fluxo Padrão")
        self.sequencia: List[str] = dados.get("sequencia", [])
        self.configuracoes: Dict[str, Any] = dados.get("configuracoes", {})
        self.indice_atual: int = 0

    @property
    def total_etapas(self) -> int:
        return len(self.sequencia)

    @property
    def id_atual(self) -> Optional[str]:
        return self.obter_id_por_indice(self.indice_atual)

    def obter_id_por_indice(self, indice: int) -> Optional[str]:
        if 0 <= indice < len(self.sequencia):
            return self.sequencia[indice]
        return None

    def avancar(self) -> bool:
        if self.indice_atual < self.total_etapas - 1:
            self.indice_atual += 1
            return True
        return False

    def retroceder(self) -> bool:
        if self.indice_atual > 0:
            self.indice_atual -= 1
            return True
        return False