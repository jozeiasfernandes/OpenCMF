from __future__ import annotations
from pathlib import Path
from PySide6 import QtWidgets
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory
from domain.volume.exporters.vti_exporter import VtiExporter


class SaveVtiTool(BaseTool):
    name: str = "save_vti"
    display_name: str = "Salvar VTI"
    category: ToolCategory = ToolCategory.TOMOGRAPHY
    icon: str = "vti.svg"  # Definição do ícone da ferramenta

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

        success = VtiExporter.save_to_vti(volume_data, Path(file_path))
        if success:
            print(f"Volume exportado com sucesso para: {file_path}")
        else:
            print("Erro ao salvar arquivo VTI.")

    def on_deactivate(self) -> None:
        pass