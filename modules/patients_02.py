from typing import Dict
from PySide6 import QtWidgets, QtCore

from modules.mod_patients_02.tabs.personal_data_tab import PersonalDataTab
from modules.mod_patients_02.validate_cep import cep_valido, consultar_cep
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

        self.project_manager = None  # placeholder

    def inicializar(self, caminho_paciente: str) -> None:
        pass

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

        return self._workspace

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {}

if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets
    from core.workspace.workspace import WorkspaceManager

    app = QtWidgets.QApplication(sys.argv)

    workspace = WorkspaceManager()

    modulo = Modulo()
    modulo.inicializar("")

    workspace.adicionar_modulo("paciente", modulo)

    workspace.resize(900, 600)
    workspace.show()

    sys.exit(app.exec())