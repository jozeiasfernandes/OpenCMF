from __future__ import annotations
from pathlib import Path
from PySide6 import QtWidgets


from core.application.scene.events.scene_events import RegistrationEvents
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory


class ImportObjectTool(BaseTool):
    name = "import_object_tool"
    display_name = "Importar"
    category = ToolCategory.OBJECTS
    icon = "add.svg"
    tool_tip = "Importar arquivos STL, VTI ou Imagens para a cena"

    def on_activate(self) -> None:
        super().on_activate()
        self._open_import_dialog()

        if self.context and hasattr(self.context, 'tool_manager'):
            self.context.tool_manager.deactivate_current_tool()

    def _get_category_from_ext(self, file_path: str) -> str:
        """Infere a categoria baseada na extensão do arquivo."""
        ext = Path(file_path).suffix.lower()
        mapping = {
            '.vti': 'volume',
            '.stl': 'surfaces',
            '.obj': 'surfaces',
            '.dcm': 'dicom',
            '.jpg': 'photos',
            '.png': 'photos'
        }
        return mapping.get(ext, 'others')

    def _open_import_dialog(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Selecionar Arquivo",
            "",
            "Arquivos Suportados (*.stl *.vti *.jpg *.png *.dcm)"
        )

        if not file_path or not self.context or not hasattr(self.context, 'event_bus'):
            return

        category = self._get_category_from_ext(file_path)

        self.context.event_bus.emit(
            RegistrationEvents.IMPORT_REQUESTED,
            file_path=file_path,
            category=category
        )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    from types import SimpleNamespace
    from unittest.mock import MagicMock


    app = QApplication(sys.argv)

    mock_event_bus = MagicMock()
    mock_tool_manager = MagicMock()

    mock_context = SimpleNamespace(
        event_bus=mock_event_bus,
        tool_manager=mock_tool_manager
    )

    tool = ImportObjectTool()
    tool.activate(mock_context)

    # Simula o fluxo de importação internamente para teste
    tool._open_import_dialog = MagicMock()
    tool.on_activate()

    if mock_event_bus.emit.called:
        print(f"\n[SUCESSO] Evento emitido: {mock_event_bus.emit.call_args}")
    else:
        print("\n[FALHA] Evento de importação não foi emitido.")

    sys.exit(0)