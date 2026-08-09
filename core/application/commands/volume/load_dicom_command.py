from __future__ import annotations
from pathlib import Path
from application.commands.base.command import Command
from domain.volume.dicom.engines.dicom_engine import DicomEngine


class LoadDicomCommand(Command):
    name = "load_dicom_command"

    def __init__(self, caminho_pasta: Path, scene_manager: Any):
        super().__init__()
        self.caminho_pasta = caminho_pasta
        self.scene_manager = scene_manager
        self.engine = DicomEngine()
        self.volume_model = None
        self.metadata.description = f"Carregar tomografia de: {caminho_pasta.name}"

    def execute(self) -> bool:
        try:
            # 1. Carrega o volume usando a engine
            self.volume_model = self.engine.carregar_volume(str(self.caminho_pasta))

            if not self.volume_model or not self.volume_model.is_valid:
                return False

            # 2. Adiciona à cena
            if self.scene_manager:
                if hasattr(self.scene_manager, "add_volume"):
                    self.scene_manager.add_volume(self.volume_model)
                elif hasattr(self.scene_manager, "objects") and hasattr(self.scene_manager.objects, "add"):
                    self.scene_manager.objects.add(self.volume_model.name, self.volume_model)
                return True

            return False
        except Exception:
            return False

    def undo(self) -> bool:
        try:
            if self.volume_model and self.scene_manager:
                # Remove o volume da cena no desfazimento
                if hasattr(self.scene_manager, "remove_volume"):
                    self.scene_manager.remove_volume(self.volume_model)
                elif hasattr(self.scene_manager, "objects") and hasattr(self.scene_manager.objects, "remove"):
                    self.scene_manager.objects.remove(self.volume_model.name)
                return True
            return False
        except Exception:
            return False