from typing import Tuple, Optional, Dict, Any, List
from PySide6 import QtWidgets, QtCore


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

    def get_main_widget(self) -> QtWidgets.QWidget:
        """Retorna o widget principal do módulo."""
        return self.viewer if self.viewer is not None else self

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna dicionário de painéis laterais (toolboxes)."""
        toolboxes: Dict[str, QtWidgets.QWidget] = {}
        toolbar = self.get_workspace_toolbar()

        if toolbar:
            toolboxes["Ferramentas"] = toolbar

        return toolboxes

    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        return None

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.viewer:
            return self.viewer

        return QtWidgets.QLabel(
            f"Workspace de {self.__class__.__name__} não carregado."
        )

    def inicializar(self, caminho_paciente: str) -> None:
        """Chamado pela orquestração do sistema."""
        self.configurar_recursos(caminho_paciente)

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