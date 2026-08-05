from __future__ import annotations
import vtk
from PySide6 import QtWidgets
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory


class SaveVtiTool(BaseTool):
    name: str = "save_vti"
    display_name: str = "Salvar VTI"
    category: ToolCategory = ToolCategory.TOMOGRAPHY

    def on_activate(self) -> None:
        self.execute_export()
        self.deactivate()

    def execute_export(self) -> None:
        if not self.context or not self.context.scene_manager:
            print("Erro: Contexto ou SceneManager não disponível para exportação.")
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Salvar Volume como VTI",
            "",
            "VTK Image Data (*.vti)"
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".vti"):
            file_path += ".vti"

        volume_data = self.context.scene_manager.get_active_volume_data()

        if not volume_data:
            print("Erro: Nenhum volume ativo encontrado para exportar.")
            return

        try:
            writer = vtk.vtkXMLImageDataWriter()
            writer.SetFileName(file_path)
            writer.SetInputData(volume_data)
            writer.SetDataModeToBinary()
            writer.SetCompressorTypeToZLib()
            writer.Write()
            print(f"Volume exportado com sucesso para: {file_path}")
        except Exception as e:
            print(f"Erro ao salvar arquivo VTI: {e}")

    def on_deactivate(self) -> None:
        pass