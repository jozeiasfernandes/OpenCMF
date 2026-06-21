import json
import importlib.util
import logging
from pathlib import Path
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class ToolbarService:
    def __init__(self, components_path: Path):
        self.components_path = components_path
        self.toolbars_path = components_path / "toolbars"
        self.tools_path = components_path / "tools"
        self.template_path = components_path.parent / "workspace" / "components_list_" / "toolbar_template.py"

    def get_all_toolbars(self) -> List[Dict]:
        toolbars = []
        if not self.toolbars_path.exists():
            logger.debug(f"Diretório de toolbars não encontrado: {self.toolbars_path}")
            return toolbars

        for path in sorted(self.toolbars_path.glob("*.py")):
            if path.name != "__init__.py":
                toolbars.append({
                    "name": self._get_toolbar_display_name(path),
                    "path": path
                })

        logger.debug(f"Carregadas {len(toolbars)} toolbars")
        return toolbars

    def get_all_tools(self) -> List[Path]:
        if not self.tools_path.exists():
            logger.debug(f"Diretório de tools não encontrado: {self.tools_path}")
            return []

        tools = [p for p in sorted(self.tools_path.glob("*.py")) if p.name != "__init__.py"]
        logger.debug(f"Carregadas {len(tools)} tools disponíveis")
        return tools

    def load_selected_tools(self, toolbar_path: Path) -> List[Path]:
        json_path = toolbar_path.with_suffix(".json")
        if not json_path.exists():
            logger.debug(f"Arquivo JSON não encontrado: {json_path}")
            return []

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                tools_data = data
            elif isinstance(data, dict) and "tools" in data:
                tools_data = data["tools"]
            else:
                logger.warning(f"Formato JSON inesperado em {json_path}")
                return []

            result = []
            for p in tools_data:
                path = Path(p)
                if not path.is_absolute():
                    path = self.components_path / path
                if path.exists():
                    result.append(path)
                else:
                    logger.warning(f"Tool não encontrada: {path}")

            logger.debug(f"Carregadas {len(result)} tools do JSON: {json_path}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON mal formatado em {json_path}: {e}")
            return []
        except IOError as e:
            logger.error(f"Erro ao ler arquivo {json_path}: {e}")
            return []

    def save_toolbar_config(self, toolbar_path: Path, tool_paths: List[Path]):
        json_path = toolbar_path.with_suffix(".json")

        try:
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

            logger.info(f"Configuração salva em: {json_path}")
            logger.debug(f"Tools salvas: {tool_paths_str}")

        except PermissionError as e:
            logger.error(f"Sem permissão para escrever em {json_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Falha ao salvar configuração: {e}")
            raise

    def create_toolbar(self, name: str):
        class_name = name.replace(" ", "").capitalize()
        file_name = name.lower().replace(" ", "_") + ".py"
        file_path = self.toolbars_path / file_name

        if file_path.exists():
            logger.error(f"Toolbar '{name}' já existe em {file_path}")
            raise FileExistsError(f"A toolbar '{name}' já existe.")

        self.toolbars_path.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            logger.error(f"Template não encontrado: {self.template_path}")
            raise FileNotFoundError(f"Template não encontrado: {self.template_path}")

        content = content.replace("{class_name}", class_name)
        content = content.replace("{name}", name)
        content = content.replace("{object_name}", file_name.replace(".py", ""))

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Arquivo .py criado: {file_path}")

        json_path = file_path.with_suffix(".json")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)
            logger.info(f"Arquivo .json criado: {json_path}")
        except Exception as e:
            logger.error(f"Erro ao criar .json: {e}")
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Arquivo .py removido para manter consistência: {file_path}")
            raise RuntimeError(f"Falha ao criar arquivo JSON: {e}")

        if file_path.exists() and json_path.exists():
            logger.info(f"Toolbar '{name}' criada com sucesso!")
            logger.debug(f"  - Python: {file_path}")
            logger.debug(f"  - JSON: {json_path}")
        else:
            logger.warning(f"Algum arquivo pode não ter sido criado corretamente para '{name}'")

    def delete_toolbar(self, toolbar_path: Path):
        for suffix in [".py", ".json", ".png"]:
            p = toolbar_path.with_suffix(suffix)
            if p.exists():
                p.unlink()
                logger.info(f"Removido: {p}")

    def _get_toolbar_display_name(self, path: Path) -> str:
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'Component'):
                return getattr(module.Component, 'toolbar_name', module.Component().windowTitle())
        except Exception as e:
            logger.debug(f"Falha ao obter nome da toolbar de {path}: {e}")
        return path.stem.replace("_", " ").title()