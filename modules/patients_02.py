import logging
from typing import Dict, Optional, Any
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.workspace.contracts import IModule

from modules.mod_patients_02.tabs.personal_data_tab import PersonalDataTab
from modules.mod_patients_02.tabs.file_list_tab import FileListTab
from modules.mod_patients_02.tabs.photo_tab import PhotoTab
from modules.mod_patients_02.tabs.project_tab import ProjectTab
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class Modulo:
    def __init__(self, project_service=None, caminho_paciente=None, **kwargs):
        """
        Injeção robusta de dependências com fallback para o serviço de projeto.
        """
        self.id = "modulo.paciente"
        self._caminho_paciente = caminho_paciente

        # Garante que project_service exista, evitando erros de atributo no futuro
        self.project_service = project_service or ProjectServiceHomePage(Path("patients"))

        # UI Principal
        self._main_widget = QtWidgets.QTabWidget()
        self._main_widget.setDocumentMode(True)

        # Instanciação das abas (Passando o serviço injetado)
        self.tab_dados = PersonalDataTab(self.project_service)
        self.tab_arquivos = FileListTab(self.project_service)
        self.tab_fotos = PhotoTab(self.project_service)
        self.tab_projeto = ProjectTab(self.project_service)

        self._main_widget.addTab(self.tab_dados, "Dados pessoais")
        self._main_widget.addTab(self.tab_arquivos, "Lista de arquivos")
        self._main_widget.addTab(self.tab_fotos, "Fotografias")
        self._main_widget.addTab(self.tab_projeto, "Projeto")

        # Conexões: Verifica se existe o atributo 'concluido' antes de conectar
        if hasattr(self.tab_dados, 'concluido'):
            self.tab_dados.concluido.connect(self._atualizar_pasta_abas)

        # Carregamento inicial
        if self._caminho_paciente:
            self._carregar_dados(self._caminho_paciente)

    def get_main_widget(self):
        """Método necessário para conformidade com a interface de módulos."""
        return self._main_widget

    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        """Opcional: Retorna uma toolbar específica do módulo[cite: 67, 72]."""
        return None

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """Retorna painéis laterais (Inspector)[cite: 67, 72]."""
        return {}

    def _carregar_dados(self, caminho: str):
        root = Path(caminho)
        dados = self.project_service.load_project(root)
        self.tab_dados.carregar(caminho)
        self.tab_arquivos.set_data(dados or {}, caminho)
        self.tab_fotos.set_data(dados or {}, caminho)
        self.tab_projeto.set_data(dados or {}, caminho)

    def _atualizar_pasta_abas(self):
        nova_pasta = self.tab_dados.pasta_paciente
        self._caminho_paciente = nova_pasta
        for tab in [self.tab_arquivos, self.tab_fotos, self.tab_projeto]:
            tab.pasta_paciente = nova_pasta

    def cleanup(self) -> None:
        """Limpeza obrigatória do IModule[cite: 67, 74]."""
        print("Limpando recursos do módulo paciente...")

import sys
from typing import Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.workspace.contracts import IModule

from modules.mod_patients_02.tabs.personal_data_tab import PersonalDataTab
from modules.mod_patients_02.tabs.file_list_tab import FileListTab
from modules.mod_patients_02.tabs.photo_tab import PhotoTab
from modules.mod_patients_02.tabs.project_tab import ProjectTab
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage


class Modulo:
    def __init__(self):
        self.id = "modulo.paciente"
        self._caminho_paciente = None
        self.project_service = ProjectServiceHomePage(Path("patients"))

        # 1. Configuração da UI (Centralizado aqui)
        self._main_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self._main_widget)
        layout.setContentsMargins(0, 0, 0, 0)

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

        # 2. Conexões de sinais
        self.tab_dados.concluido.connect(self._atualizar_pasta_abas)
        self.tab_projeto.importacao_concluida.connect(lambda: print("Projeto Importado"))

    def get_main_widget(self) -> QtWidgets.QWidget:
        """Contrato IModule: Retorna o widget principal."""
        return self._main_widget

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """Contrato IModule: Retorna side_panel_container ou painéis extras."""
        # Se desejar manter o botão 'Salvar' visível, pode colocá-lo em um painel aqui
        return {}

    def inicializar(self, caminho_paciente: str) -> None:
        self._caminho_paciente = caminho_paciente
        root = Path(caminho_paciente)
        dados = self.project_service.load_project(root)

        self.tab_dados.carregar(caminho_paciente)
        self.tab_arquivos.set_data(dados or {}, caminho_paciente)
        self.tab_fotos.set_data(dados or {}, caminho_paciente)
        self.tab_projeto.set_data(dados or {}, caminho_paciente)

    def _atualizar_pasta_abas(self):
        nova_pasta = self.tab_dados.pasta_paciente
        self._caminho_paciente = nova_pasta

        for tab in [self.tab_arquivos, self.tab_fotos, self.tab_projeto]:
            tab.pasta_paciente = nova_pasta

    def validar_passagem(self) -> bool:
        if not self._caminho_paciente:
            return True
        root = Path(self._caminho_paciente)
        data = self.project_service.load_project(root) or {}
        data["caminhos"] = self.tab_arquivos.get_data()
        data["fotos"] = self.tab_fotos.get_data()
        self.project_service.save_project(root, data)
        return True

    def cleanup(self) -> None:
        """Contrato IModule: Limpeza de recursos."""
        print("Limpando recursos do módulo paciente...")


if __name__ == "__main__":
    from core.workspace.workspace_manager import WorkspaceManager

    app = QtWidgets.QApplication(sys.argv)

    window = WorkspaceManager()

    modulo = Modulo()

    window.central_host.addWidget(modulo.get_main_widget())
    window.central_host.setCurrentWidget(modulo.get_main_widget())

    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())