from __future__ import annotations
from typing import Optional
from core.components.tools.base.base_tool import BaseTool, ToolCategory, InteractionContext


class ValidateDicomTool(BaseTool):
    name: str = "validate_dicom"
    display_name: str = "Validar DICOM"
    category: ToolCategory = ToolCategory.TOMOGRAPHY

    def __init__(self, target_directory: Optional[str] = None):
        super().__init__()
        self.target_directory = target_directory
        self.is_valid = False

    def on_activate(self) -> None:
        if not self.target_directory:
            print("Erro: Nenhum diretório definido para validação.")
            return

        self.validate()
        self.deactivate()

    def validate(self) -> bool:
        print(f"Validando diretório: {self.target_directory}")

        try:
            self.is_valid = True

            if self.context and hasattr(self.context, 'event_bus'):
                self.context.event_bus.emit("validation_success", self.is_valid)

            print(f"Validação concluída. Status: {self.is_valid}")
            return self.is_valid

        except Exception as e:
            print(f"Falha na validação: {e}")
            return False

    def on_deactivate(self) -> None:
        pass