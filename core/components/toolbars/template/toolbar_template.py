from typing import Optional, TYPE_CHECKING
import json
import importlib.util
import inspect
import logging
import traceback
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.components.bases.base_tool.base_tool import BaseTool
from core.components.bases.base_tool.base_toolbar_handler import ToolManager

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager

logger = logging.getLogger("ToolbarLoader")

class {class_name}Handler(BaseToolbarHandler): # Certifique-se que BaseToolbarHandler esteja correto
    def __init__(self, toolbar: BaseToolbar, tool_manager: ToolManager, scene_manager: Optional["SceneManager"] = None):
        super().__init__(toolbar, tool_manager=tool_manager)
        self._scene_manager = scene_manager
        self.json_path = Path(__file__).resolve().with_suffix(".json")
        self._setup_ui()

    def _setup_ui(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        self.load_tools_from_json()

    def load_tools_from_json(self) -> None:
        self.clear_toolbar()
        if not self.json_path.exists():
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                tool_paths: list[str] = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler JSON: {e}")
            return

        for path_str in tool_paths:
            full_path = self._resolve_tool_path(path_str)
            if full_path and full_path.exists():
                tool_instance = self._instanciar_tool(full_path)
                if tool_instance:
                    self.register_tool(tool_instance)

    def _resolve_tool_path(self, path_str: str) -> Optional[Path]:
        candidate = Path(path_str)
        for p in [candidate, self.root_path / candidate, self.root_path / "tools" / candidate.name]:
            if p.exists(): return p.resolve()
        return None

    def _instanciar_tool(self, path: Path) -> Optional[BaseTool]:
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj is not BaseTool:
                    # Injeta o scene_manager se necessário
                    return obj(scene_manager=self._scene_manager) if self._scene_manager else obj()
        except Exception:
            logger.error(f"Falha ao instanciar tool {path.name}:\n{traceback.format_exc()}")
        return None


class {class_name}(BaseToolbar):
    # Usamos o atributo de classe para o loader identificar o componente
    toolbox_name = "{name}"

    def __init__(self, modulo: Any = None, tool_manager: ToolManager = None, scene_manager: Optional["SceneManager"] = None):
        # Passamos tudo para a BaseToolbar (que agora injeta modulo e scene_manager)
        super().__init__(
            title=self.toolbox_name,
            modulo=modulo,
            scene_manager=scene_manager
        )
        self.setObjectName("{object_name}")
        self.handler = {class_name}Handler(self, tool_manager=tool_manager, scene_manager=scene_manager)

    def setup_ui(self):
        # A lógica de UI específica vai aqui, conforme exigido pela BaseToolbar
        pass

    def refresh(self):
        self.handler.load_tools_from_json()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main_window = QtWidgets.QMainWindow()
    toolbar = Component()
    main_window.addToolBar(toolbar)

    main_window.setWindowTitle("Debug Toolbar: {name}")
    main_window.resize(400, 100)
    main_window.show()

    sys.exit(app.exec())