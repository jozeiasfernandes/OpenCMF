from __future__ import annotations
from typing import Optional
from PySide6 import QtWidgets
from core.components.tools.base.base_tool import BaseTool
from core.scene.events.scene_events import OBJECT_ADDED


class ImportObjectTool(BaseTool):
    name = "import_object_tool"
    display_name = "Importar"
    icon = "add.svg"
    tool_tip = "Importar arquivos STL, VTI ou Imagens para a cena"

    def on_activate(self) -> None:
        self._open_import_dialog()
        self.deactivate()

    def _open_import_dialog(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Selecionar Arquivo",
            "",
            "Arquivos Suportados (*.stl *.vti *.jpg *.png *.dcm)"
        )
        if not file_path or not self.context or not self.context.scene_manager:
            return

        object_manager = getattr(self.context, 'object_manager', None)
        if object_manager:
            object_manager.import_external_file(file_path, "surfaces")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    from types import SimpleNamespace
    from unittest.mock import MagicMock
    from core.components.tools.base.base_tool import InteractionContext

    app = QApplication(sys.argv)

    mock_context = SimpleNamespace(
        renderer=MagicMock(),
        interactor=MagicMock(),
        scene_manager=MagicMock(),
        object_manager=MagicMock()  # Agora funcionará sem erro de atributo
    )

    mock_context.scene_manager = MagicMock()
    mock_context.object_manager = MagicMock()

    tool = ImportObjectTool()
    tool.activate(mock_context)

    print("Ferramenta ImportObjectTool instanciada e pronta para teste.")