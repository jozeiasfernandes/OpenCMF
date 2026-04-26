from PySide6 import QtWidgets, QtCore
from typing import Tuple, Optional, Dict, Any, List

class ModuloBase(QtWidgets.QWidget):
    concluido = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.pasta_paciente: Optional[str] = None

    def inicializar(self, caminho_paciente: str) -> None:
        self.pasta_paciente = caminho_paciente
        self.configurar_recursos()

    def configurar_recursos(self) -> None:
        pass

    def verificar_pre_requisitos(self) -> Tuple[bool, str]:
        return True, ""

    def validar_passagem(self) -> bool:
        return True

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        return None

    def get_workspace(self) -> QtWidgets.QWidget:
        if hasattr(self, 'viewer'):
            return self.viewer
        return QtWidgets.QLabel(f"Workspace de {self.__class__.__name__} não carregado.")

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {}


class FluxoBase:
    def __init__(self, dados: Dict[str, Any]):
        self.nome: str = dados.get('nome', 'Fluxo Padrão')
        self.sequencia: List[str] = dados.get('sequencia', [])
        self.configuracoes: Dict[str, Any] = dados.get('configuracoes', {})
        self.indice_atual: int = 0

    @property
    def total_etapas(self) -> int:
        return len(self.sequencia)

    @property
    def id_atual(self) -> Optional[str]:
        if not self.sequencia:
            return None
        return self.obter_id_por_indice(self.indice_atual)

    def obter_id_por_indice(self, indice: int) -> Optional[str]:
        if 0 <= indice < len(self.sequencia):
            return self.sequencia[indice]
        return None