import json
import importlib.util
from pathlib import Path
from typing import List, Optional, Dict


class ToolbarService:
    def __init__(self, components_path: Path):
        self.components_path = components_path
        self.toolbars_path = components_path / "toolbars"
        self.tools_path = components_path / "tools"
        self.template_path = components_path.parent / "workspace" / "components_list_" / "toolbar_template.py"

    def get_all_toolbars(self) -> List[Dict]:
        """Retorna uma lista de dicts com nome e caminho de cada toolbar."""
        toolbars = []
        if not self.toolbars_path.exists():
            return toolbars

        for path in sorted(self.toolbars_path.glob("*.py")):
            if path.name != "__init__.py":
                toolbars.append({
                    "name": self._get_toolbar_display_name(path),
                    "path": path
                })
        return toolbars

    def get_all_tools(self) -> List[Path]:
        """Retorna todos os arquivos de tools disponíveis."""
        if not self.tools_path.exists():
            return []
        return [p for p in sorted(self.tools_path.glob("*.py")) if p.name != "__init__.py"]

    def load_selected_tools(self, toolbar_path: Path) -> List[Path]:
        """Lê o arquivo JSON associado à toolbar."""
        json_path = toolbar_path.with_suffix(".json")
        if not json_path.exists():
            return []
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return [Path(p) for p in json.load(f) if Path(p).exists()]
        except (json.JSONDecodeError, IOError):
            return []

    def save_toolbar_config(self, toolbar_path: Path, tool_paths: List[Path]):
        """Salva a lista de tools no JSON da toolbar."""
        json_path = toolbar_path.with_suffix(".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([str(t) for t in tool_paths], f, indent=4)

    def create_toolbar(self, name: str):
        """Cria os arquivos base de uma nova toolbar."""
        class_name = name.replace(" ", "").capitalize()
        file_name = name.lower().replace(" ", "_") + ".py"
        file_path = self.toolbars_path / file_name

        if file_path.exists():
            raise FileExistsError(f"A toolbar '{name}' já existe.")

        # Ler o template
        with open(self.template_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Substituir manualmente (mais seguro que format)
        content = content.replace("{class_name}", class_name)
        content = content.replace("{name}", name)
        content = content.replace("{object_name}", file_name.replace(".py", ""))

        # Salvar
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    def delete_toolbar(self, toolbar_path: Path):
        """Remove os arquivos .py, .json e .png associados."""
        for suffix in [".py", ".json", ".png"]:
            p = toolbar_path.with_suffix(suffix)
            if p.exists():
                p.unlink()

    def _get_toolbar_display_name(self, path: Path) -> str:
        """Extrai o nome da toolbar dinamicamente (fallback para nome do arquivo)."""
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'Component'):
                return getattr(module.Component, 'toolbar_name', module.Component().windowTitle())
        except Exception:
            pass
        return path.stem.replace("_", " ").title()