from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore

from modules.mod_patients_02.tabs.personal_data_tab import PersonalDataTab
from modules.mod_patients_02.tabs.file_list_tab import FileListTab
from modules.mod_patients_02.tabs.photo_tab import PhotoTab


class Modulo(QtWidgets.QWidget):
    concluido = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.nome = "Paciente"
        self.id = "modulo.paciente"

        self._workspace = None
        self._toolbar = None

        self.project_manager = None
        self._caminho_paciente = None

        self.tabs = None
        self.tab_dados = None

    def set_project_manager(self, manager):
        self.project_manager = manager

        # mantém sincronizado se já foi criado
        if self.tab_dados:
            self.tab_dados.project_manager = manager

    def inicializar(self, caminho_paciente: str) -> None:
        self._caminho_paciente = caminho_paciente

        if self.tab_dados:
            self.tab_dados.carregar(caminho_paciente)

    def verificar_pre_requisitos(self):
        if not self.project_manager:
            return False, "ProjectManager não definido"
        return True, ""

    def validar_passagem(self) -> bool:
        return True

    def _ensure_project_manager(self):
        if self.project_manager:
            return

        from core.project.project_manager import ProjectManager
        from pathlib import Path

        self.project_manager = ProjectManager(
            Path("patients"),
            Path("fluxos")
        )

    def get_workspace_toolbar(self) -> QtWidgets.QWidget:
        if self._toolbar:
            return self._toolbar

        self._toolbar = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(self._toolbar)
        layout.setContentsMargins(0, 0, 0, 2)
        layout.addStretch()

        return self._toolbar

    def get_workspace(self) -> QtWidgets.QWidget:
        if self._workspace:
            return self._workspace

        # garante funcionamento mesmo sem injection
        self._ensure_project_manager()

        self._workspace = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(self._workspace)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)

        self.tab_dados = PersonalDataTab(self.project_manager)
        self.tab_arquivos = FileListTab()
        self.tab_fotos = PhotoTab()
        self.tab_projeto = QtWidgets.QWidget()

        self.tabs.addTab(self.tab_dados, "Dados pessoais")
        self.tabs.addTab(self.tab_arquivos, "Lista de arquivos")
        self.tabs.addTab(self.tab_fotos, "Fotografias")
        self.tabs.addTab(self.tab_projeto, "Projeto")

        layout.addWidget(self.tabs)

        if self._caminho_paciente:
            self.tab_dados.carregar(self._caminho_paciente)

        return self._workspace

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {}