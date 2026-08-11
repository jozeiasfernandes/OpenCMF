from __future__ import annotations
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory
from domain.volume.exporters.vti_exporter import VtiExporter

# Settings
from core.settings.localization.translator import tr


class SaveVtiTool(BaseTool):
    name: str = "save_vti"
    display_name: str = tr("import.volumes.volume_vti", "Salvar VTI")
    category: ToolCategory = ToolCategory.TOMOGRAPHY
    icon: str = "vti.svg"
    tool_tip: str = "Salvar volume atual no formato VTI"

    def create_widget(self) -> QtWidgets.QWidget:
        """Cria e retorna o widget personalizado com o texto 'Salvar volume' seguido do ícone."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        layout.addWidget(QtWidgets.QLabel(tr("import.volumes.volume_vti", "Salvar volume")))

        icon_btn = QtWidgets.QToolButton()
        icon_btn.setToolTip(self.tool_tip)
        icon_btn.setIcon(self.get_qicon())
        icon_btn.setCheckable(False)
        icon_btn.clicked.connect(self.execute_export)
        layout.addWidget(icon_btn)

        return container

    def on_activate(self) -> None:
        self.execute_export()
        QtCore.QTimer.singleShot(0, self.deactivate)

    def execute_export(self) -> None:
        if not self.context or not self.context.scene_manager:
            print("Erro: Contexto ou SceneManager não disponível para exportação.")
            return

        parent_window = self.context.window if hasattr(self.context, "window") else None

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent_window,
            tr("dialogs.import.title", "Salvar Volume como VTI"),
            "",
            tr("dialogs.filter.supported", "VTK Image Data (*.vti)")
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


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    tool = SaveVtiTool()
    sys.exit(app.exec())