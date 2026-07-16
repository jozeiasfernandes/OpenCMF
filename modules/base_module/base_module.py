from typing import Tuple, Optional, Dict, Any, List
from PySide6 import QtWidgets, QtCore


class ModuloBase(QtWidgets.QWidget):
    concluido = QtCore.Signal()

    def __init__(self, scene_manager: Optional[Any] = None, parent: Optional[QtWidgets.QWidget] = None, **kwargs):
        super().__init__(parent=parent)

        self.scene_manager = scene_manager
        self.project_service = kwargs.get("project_service")
        self.pasta_paciente = kwargs.get("pasta_paciente")

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.viewer: Optional[QtWidgets.QWidget] = None


    def get_main_widget(self) -> QtWidgets.QWidget:
        """Retorna o widget principal. Se não existir, retorna o próprio módulo."""
        return self.viewer if self.viewer is not None else self

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """
        Mantém compatibilidade com o contrato. Se o módulo legado tiver
        uma barra de ferramentas, podemos incluí-la aqui como um dicionário.
        """
        toolboxes = {}
        # Caso exista um método legado de toolbar_container, transformamos em toolbox
        toolbar = self.get_workspace_toolbar()
        if toolbar:
            toolboxes["Ferramentas"] = toolbar
        return toolboxes

    # --- Estrutura Base e Métodos Legados ---

    def inicializar(self, caminho_paciente: str) -> None:
        self.pasta_paciente = caminho_paciente
        self.configurar_recursos()

    def cleanup(self) -> None:
        pass

    def configurar_recursos(self) -> None:
        pass

    def verificar_pre_requisitos(self) -> Tuple[bool, str]:
        return True, ""

    def validar_passagem(self) -> bool:
        return True

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        return None

    def get_workspace(self) -> QtWidgets.QWidget:
        if hasattr(self, "viewer"):
            return self.viewer
        return QtWidgets.QLabel(f"Workspace de {self.__class__.__name__} não carregado.")


class FluxoBase:
    # (Mantido como você definiu, pois está bem estruturado)
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