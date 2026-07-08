from __future__ import annotations
from PySide6 import QtWidgets
from core.components.tools.base.base_tool import BaseTool


class ImportObjectTool(BaseTool):
    name = "import_object_tool"
    display_name = "Importar"
    icon = "add.svg"
    tool_tip = "Importar arquivos STL, VTI ou Imagens para a cena"

    def on_activate(self) -> None:
        super().on_activate()
        self._open_import_dialog()

        if self.context and hasattr(self.context, 'tool_manager'):
            self.context.tool_manager.deactivate_current_tool()

    def _open_import_dialog(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Selecionar Arquivo",
            "",
            "Arquivos Suportados (*.stl *.vti *.jpg *.png *.dcm)"
        )

        if not file_path or not self.context or not hasattr(self.context, 'event_bus'):
            return

        # IMPORTAÇÃO LOCAL: Resolve o ciclo de dependência e evita o ImportError
        from core.scene.events.scene_events import RegistrationEvents

        self.context.event_bus.emit(
            RegistrationEvents.IMPORT_REQUESTED,
            file_path=file_path,
            category="surfaces"
        )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    # Mova o import para DENTRO do bloco ou use uma importação local
    # para que o script não tente carregar o pacote core inteiro ao iniciar

    app = QApplication(sys.argv)

    mock_event_bus = MagicMock()
    mock_tool_manager = MagicMock()

    mock_context = SimpleNamespace(
        event_bus=mock_event_bus,
        tool_manager=mock_tool_manager
    )

    tool = ImportObjectTool()
    tool.activate(mock_context)

    # Verifica o evento usando a string direta ou o import local
    # para evitar erro de carregamento do sistema
    from core.scene.events import RegistrationEvents

    if mock_event_bus.emit.called:
        print(f"\n[SUCESSO] Evento emitido: {mock_event_bus.emit.call_args}")
    else:
        print("\n[FALHA] Evento de importação não foi emitido.")

    sys.exit(0)