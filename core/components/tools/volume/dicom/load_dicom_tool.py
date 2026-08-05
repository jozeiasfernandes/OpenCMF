from __future__ import annotations
from typing import Optional
from PySide6 import QtWidgets
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory


class OpenDicomTool(BaseTool):
    name: str = "open_dicom"
    display_name: str = "Abrir DICOM"
    category: ToolCategory = ToolCategory.TOMOGRAPHY

    def __init__(self):
        super().__init__()
        self.directory: Optional[str] = None

    def on_activate(self) -> None:
        self.execute_import()
        self.deactivate()

    def execute_import(self) -> None:
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Selecionar Pasta DICOM",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        if directory:
            self.directory = directory
            print(f"Diretório selecionado: {self.directory}")
            self.process_dicom(self.directory)

    def process_dicom(self, path: str) -> None:
        if self.context and self.context.scene_manager:
            print(f"Carregando volume via SceneManager em: {path}")
        else:
            print("Erro: Contexto ou SceneManager não disponível.")

    def on_deactivate(self) -> None:
        print("Ferramenta de importação DICOM desativada.")