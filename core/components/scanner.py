import inspect
import importlib.util
from pathlib import Path
from typing import Optional, Type
from core.components.registry import ComponentRegistry, ComponentMetadata, ComponentType
from core.components.bases.base_component import BaseComponent


class ComponentScanner:
    # Mapeamento para saber onde procurar cada tipo de componente
    COMPONENT_MAPPING = {
        "tools": ComponentType.TOOL,
        "side_panel_container": ComponentType.SIDE_PANEL,
        "central_area": ComponentType.CENTRAL_AREA,
        "toolbars": ComponentType.TOOLBAR
    }

    def __init__(self, components_path: Path):
        self.components_path = components_path
        self.registry = ComponentRegistry()

    def scan_all(self):
        """Escaneia todos os diretórios definidos no mapeamento."""
        for folder_name, comp_type in self.COMPONENT_MAPPING.items():
            folder_path = self.components_path / folder_name
            if folder_path.exists():
                self._scan_folder(folder_path, comp_type)

    def _scan_folder(self, folder_path: Path, comp_type: ComponentType):
        for file_path in folder_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            metadata = self._extract_metadata(file_path, comp_type)
            if metadata:
                self.registry.register_component(metadata)

    def _extract_metadata(self, file_path: Path, comp_type: ComponentType) -> Optional[ComponentMetadata]:
        try:
            # Importação dinâmica para introspecção
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Procura por uma classe que herde de BaseComponent
            class_name = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseComponent) and obj is not BaseComponent:
                    class_name = name
                    break

            if not class_name:
                return None

            return ComponentMetadata(
                path=file_path,
                display_name=file_path.stem.replace("_", " ").title(),
                component_type=comp_type,
                class_name=class_name
            )
        except Exception as e:
            print(f"Erro ao escanear {file_path.name}: {e}")
            return None