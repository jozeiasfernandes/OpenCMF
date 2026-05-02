import sys
from typing import Dict
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from modules.mod_patients_02.tabs.personal_data_tab import PersonalDataTab
from modules.mod_patients_02.tabs.file_list_tab import FileListTab
from modules.mod_patients_02.tabs.photo_tab import PhotoTab
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage


class Modulo(QtWidgets.QWidget):
    concluido = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.nome = "Paciente"
        self.id = "modulo.paciente"
        self.project_service = ProjectServiceHomePage(Path("patients"))

        self._workspace = None
        self._toolbar = None
        self._caminho_paciente = None

        self.tab_dados = None
        self.tab_arquivos = None
        self.tab_fotos = None

    def inicializar(self, caminho_paciente: str) -> None:
        self._caminho_paciente = caminho_paciente
        root = Path(caminho_paciente)
        dados = self.project_service.load_project(root)

        if self.tab_dados:
            self.tab_dados.carregar(caminho_paciente)

        if self.tab_arquivos:
            self.tab_arquivos.set_data(dados or {}, caminho_paciente)

        if self.tab_fotos:
            self.tab_fotos.set_data(dados or {}, caminho_paciente)

    def _atualizar_pasta_abas(self):
        """Sincroniza a pasta do paciente entre as abas após o primeiro salvamento."""
        if self.tab_dados:
            nova_pasta = self.tab_dados.pasta_paciente
            self._caminho_paciente = nova_pasta

            if self.tab_arquivos:
                self.tab_arquivos.pasta_paciente = nova_pasta
            if self.tab_fotos:
                self.tab_fotos.pasta_paciente = nova_pasta

    def verificar_pre_requisitos(self):
        return True, ""

    def validar_passagem(self) -> bool:
        if not self._caminho_paciente:
            return True

        root = Path(self._caminho_paciente)
        data = self.project_service.load_project(root) or {}

        if self.tab_arquivos:
            data["caminhos"] = self.tab_arquivos.get_data()

        if self.tab_fotos:
            data["fotos"] = self.tab_fotos.get_data()

        self.project_service.save_project(root, data)
        return True

    def get_workspace_toolbar(self) -> QtWidgets.QWidget:
        if not self._toolbar:
            self._toolbar = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(self._toolbar)
            layout.setContentsMargins(0, 0, 0, 2)

            btn_salvar = QtWidgets.QPushButton("Salvar Alterações")
            btn_salvar.clicked.connect(self.validar_passagem)

            layout.addStretch()
            layout.addWidget(btn_salvar)
        return self._toolbar

    def get_workspace(self) -> QtWidgets.QWidget:
        if self._workspace:
            return self._workspace

        self._workspace = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self._workspace)
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QtWidgets.QTabWidget()
        tabs.setDocumentMode(True)

        self.tab_dados = PersonalDataTab(self.project_service)
        self.tab_arquivos = FileListTab(self.project_service)
        self.tab_fotos = PhotoTab(self.project_service)

        # Conecta o sinal de conclusão (salvamento) dos dados para atualizar as outras abas
        self.tab_dados.concluido.connect(self._atualizar_pasta_abas)

        tabs.addTab(self.tab_dados, "Dados pessoais")
        tabs.addTab(self.tab_arquivos, "Lista de arquivos")
        tabs.addTab(self.tab_fotos, "Fotografias")

        layout.addWidget(tabs)

        if self._caminho_paciente:
            self.inicializar(self._caminho_paciente)

        return self._workspace

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    modulo = Modulo()
    window.setCentralWidget(modulo.get_workspace())
    window.setMenuWidget(modulo.get_workspace_toolbar())
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())