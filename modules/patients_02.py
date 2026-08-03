import sys
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
from PySide6 import QtWidgets, QtCore

# Tabs
from modules.mod_patients_02.tabs.personal_data_tab import PersonalDataTab
from modules.mod_patients_02.tabs.file_list_tab import FileListTab
from modules.mod_patients_02.tabs.photo_tab import PhotoTab
from modules.mod_patients_02.tabs.project_tab import ProjectTab

# Patient
from core.patient.patient_manager import PatientManager
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage

# Settings
from list_paths import PATIENTS_DIR


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

    def get_central_area(self) -> QtWidgets.QWidget:
        """Retorna o widget principal do módulo (Área central)."""
        return self.viewer if self.viewer is not None else self

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        """Módulo sem painel lateral."""
        return {}

    def get_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        """Módulo sem barra de ferramentas."""
        return None

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


class Modulo(ModuloBase):
    def __init__(self, context: Any = None, caminho_paciente: str = None, **kwargs):
        super().__init__(context=context)
        self.id = "modulo.paciente"
        self.nome = "Paciente"

        # Inicialização do serviço de projetos com o diretório correto
        self.project_service = ProjectServiceHomePage(PATIENTS_DIR)

        # Obtenção do Singleton do PatientManager injetando o project_service
        self.patient_manager = PatientManager.get_instance(self.project_service)

        self._caminho_paciente = caminho_paciente or self.patient_manager.current_path

        # 1. Configuração da UI
        layout = self.layout()

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)

        self.tab_dados = PersonalDataTab(self.project_service)
        self.tab_arquivos = FileListTab(self.project_service)
        self.tab_fotos = PhotoTab(self.project_service)
        self.tab_projeto = ProjectTab(self.project_service)

        self.tabs.addTab(self.tab_dados, "Dados pessoais")
        self.tabs.addTab(self.tab_arquivos, "Lista de arquivos")
        self.tabs.addTab(self.tab_fotos, "Fotografias")
        self.tabs.addTab(self.tab_projeto, "Projeto")

        layout.addWidget(self.tabs)
        self.viewer = self

        # 2. Conexões de sinais reativos e de UI
        if hasattr(self.tab_dados, 'concluido'):
            self.tab_dados.concluido.connect(self._atualizar_pasta_abas)

        if hasattr(self.tab_projeto, 'importacao_concluida'):
            self.tab_projeto.importacao_concluida.connect(lambda: print("Projeto Importado"))

        # Conecta aos sinais do PatientManager para atualização reativa automática
        self.patient_manager.patient_changed.connect(self._on_patient_changed)
        self.patient_manager.patient_data_loaded.connect(self._on_patient_data_loaded)

        # Carregamento inicial se o caminho for fornecido
        if self._caminho_paciente:
            self.inicializar(self._caminho_paciente)

    def configurar_recursos(self, caminho_paciente: str) -> None:
        """Configura os recursos garantindo sincronia com o PatientManager."""
        if not caminho_paciente:
            return

        self._caminho_paciente = caminho_paciente

        # Atualiza o estado global se ainda não estiver configurado lá
        if self.patient_manager.current_path != caminho_paciente:
            self.patient_manager.set_active_patient(caminho_paciente)
            return  # O sinal _on_patient_data_loaded cuidará de atualizar as abas

        dados = self.patient_manager.data or self.project_service.load_project(Path(caminho_paciente)) or {}

        self.tab_dados.carregar(caminho_paciente)
        self.tab_arquivos.set_data(dados, caminho_paciente)
        self.tab_fotos.set_data(dados, caminho_paciente)
        self.tab_projeto.set_data(dados, caminho_paciente)

    def _on_patient_changed(self, caminho: str):
        """Callback acionado reativamente quando o PatientManager altera o paciente ativo."""
        if caminho and caminho != self._caminho_paciente:
            self._caminho_paciente = caminho
            self.configurar_recursos(caminho)

    def _on_patient_data_loaded(self, dados: dict):
        """Callback acionado reativamente quando novos dados do paciente são carregados."""
        if self._caminho_paciente:
            self.tab_dados.carregar(self._caminho_paciente)
            self.tab_arquivos.set_data(dados, self._caminho_paciente)
            self.tab_fotos.set_data(dados, self._caminho_paciente)
            self.tab_projeto.set_data(dados, self._caminho_paciente)

    def _atualizar_pasta_abas(self):
        nova_pasta = self.tab_dados.pasta_paciente
        if nova_pasta:
            self.patient_manager.set_active_patient(nova_pasta)

    def validar_passagem(self) -> bool:
        if not self._caminho_paciente:
            return True
        root = Path(self._caminho_paciente)

        # Sincroniza os dados atuais do PatientManager com as modificações das abas
        data = self.patient_manager.data.copy() or self.project_service.load_project(root) or {}
        data["caminhos"] = self.tab_arquivos.get_data()
        data["fotos"] = self.tab_fotos.get_data()

        self.project_service.save_project(root, data)
        self.patient_manager.set_active_patient(str(root))
        return True

    def cleanup(self) -> None:
        """Contrato IModule: Limpeza de recursos."""
        print("Limpando recursos do módulo paciente...")


if __name__ == "__main__":
    from core.workspace.workspace_manager import WorkspaceManager

    app = QtWidgets.QApplication(sys.argv)

    window = WorkspaceManager()

    from core.workspace.models.module_factory import ModuleFactory

    ModuleFactory.register("modulo.paciente", Modulo)

    modulo = ModuleFactory.create("modulo.paciente")

    window.header.add_module_tab("modulo.paciente", modulo.nome)
    window.central_manager.set_view(modulo.get_central_area())

    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())