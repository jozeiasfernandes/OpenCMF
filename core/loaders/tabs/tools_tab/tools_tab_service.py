import json
import importlib.util
import logging
from pathlib import Path
from typing import List, Dict
from core.components.toolbars.utils.capture_toolbar_png import capture_toolbar_screenshot
from core.components.bases.base_tool import ToolCategory

logger = logging.getLogger(__name__)

class ToolbarService:
    def __init__(self, components_path: Path):
        self.components_path = components_path
        self.toolbars_path = components_path / "toolbars"
        self.tools_path = components_path / "tools"
        self.template_path = components_path.parent / "components" / "toolbars" / "template" / "toolbar_template.py"


    def get_all_toolbars(self) -> List[Dict]:
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
        if not self.tools_path.exists():
            return []
        return [p for p in sorted(self.tools_path.glob("*.py")) if p.name != "__init__.py"]

    def load_selected_tools(self, toolbar_path: Path) -> List[Path]:
        json_path = toolbar_path.with_suffix(".json")
        if not json_path.exists():
            return []

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            tools_data = data if isinstance(data, list) else data.get("tools", [])

            result = []
            for p in tools_data:
                path = Path(p)
                if not path.is_absolute():
                    path = self.components_path / path
                if path.exists():
                    result.append(path)
            return result
        except (json.JSONDecodeError, IOError):
            return []

    def save_toolbar_config(self, toolbar_path: Path, tool_paths: List[Path]):
        json_path = toolbar_path.with_suffix(".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)

        tool_paths_str = []
        for t in tool_paths:
            try:
                rel_path = t.relative_to(self.components_path)
                tool_paths_str.append(str(rel_path))
            except ValueError:
                tool_paths_str.append(str(t))

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(tool_paths_str, f, indent=4, ensure_ascii=False)

    def add_tool_to_toolbar(self, toolbar_path: Path, new_tool_path: Path):
        current_tools = self.load_selected_tools(toolbar_path)

        if new_tool_path.resolve() not in [t.resolve() for t in current_tools]:
            current_tools.append(new_tool_path)
            self.save_toolbar_config(toolbar_path, current_tools)

    def create_toolbar(self, name: str):
        class_name = name.replace(" ", "").capitalize()
        file_name = name.lower().replace(" ", "_") + ".py"
        file_path = self.toolbars_path / file_name

        if file_path.exists():
            raise FileExistsError(f"A toolbar '{name}' já existe.")

        self.toolbars_path.mkdir(parents=True, exist_ok=True)
        with open(self.template_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = content.replace("{class_name}", class_name).replace("{name}", name).replace("{object_name}", file_name.replace(".py", ""))
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        if file_path.exists():
            capture_toolbar_screenshot(file_path)

        json_path = file_path.with_suffix(".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

    def delete_toolbar(self, toolbar_path: Path):
        for suffix in [".py", ".json", ".png"]:
            p = toolbar_path.with_suffix(suffix)
            if p.exists():
                p.unlink()

    def _get_toolbar_display_name(self, path: Path) -> str:
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'Registration_SidePanel'):
                return getattr(module.Component, 'toolbar_name', module.Component().windowTitle())
        except Exception:
            pass
        return path.stem.replace("_", " ").title()

    def get_all_tools_with_metadata(self):
        tools_list = []
        for path in self.get_all_tools():
            tool_class = self._instanciar_tool(path)
            if tool_class:
                tools_list.append({
                    "path": path,
                    "display_name": getattr(tool_class, "display_name", "Desconhecido"),
                    "category": getattr(tool_class, "category", ToolCategory.OTHER)
                })
        return tools_list

    def _instanciar_tool(self, path):
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                obj = getattr(module, attr_name)

                if isinstance(obj, type) and hasattr(obj, 'category') and obj.__name__ != 'BaseTool':
                    return obj
        except Exception as e:
            logger.error(f"Falha ao instanciar tool {path.name}: {e}")
        return None