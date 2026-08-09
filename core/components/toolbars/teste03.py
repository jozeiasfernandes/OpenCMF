from typing import Optional, TYPE_CHECKING
import json
import importlib.util
import inspect
import logging
import traceback
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_toolbar.base_toolbar import BaseToolbar
from core.components.bases.base_component import AppContext

if TYPE_CHECKING:
    pass

logger = logging.getLogger("ToolbarLoader")


class Teste03Handler:
    """Gerencia a carga e registro dinâmico de ferramentas a partir de um JSON."""

    def __init__(self, toolbar: "Teste03", app_context: AppContext):
        self.toolbar = toolbar
        self.app_context = app_context
        self.root_path = Path(__file__).resolve().parent
        self.json_path = self.root_path / f"{{class_name.lower()}}.json"  # ou with_suffix(".json")
        self._setup_ui()

    def _setup_ui(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        self.load_tools_from_json()

    def load_tools_from_json(self) -> None:
        self.toolbar.clear()
        if not self.json_path.exists():
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                tool_paths: list[str] = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler JSON da toolbar: {e}")
            return

        for path_str in tool_paths:
            full_path = self._resolve_tool_path(path_str)
            if full_path and full_path.exists():
                tool_instance = self._instanciar_tool(full_path)
                if tool_instance:
                    self.toolbar.register_tool(tool_instance)

    def _resolve_tool_path(self, path_str: str) -> Optional[Path]:
        candidate = Path(path_str)
        for p in [candidate, self.root_path / candidate, self.root_path / "tools" / candidate.name]:
            if p.exists():
                return p.resolve()
        return None

    def _instanciar_tool(self, path: Path) -> Optional[BaseTool]:
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            if not spec or not spec.loader:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj is not BaseTool:
                    # Injeta o app_context ou scene_manager dependendo de como a BaseTool foi construída
                    sig = inspect.signature(obj.__init__)
                    if "app_context" in sig.parameters:
                        return obj(app_context=self.app_context)
                    elif "scene_manager" in sig.parameters:
                        return obj(scene_manager=self.app_context.scene_manager)
                    else:
                        return obj()
        except Exception:
            logger.error(f"Falha ao instanciar tool {path.name}:\n{traceback.format_exc()}")
        return None


class Teste03(BaseToolbar):
    toolbox_name = "Teste03"

    def __init__(self, app_context: AppContext, parent: Optional[QtWidgets.QWidget] = None):
        # Repassa o app_context exigido pela nova BaseToolbar
        super().__init__(
            title=self.toolbox_name,
            app_context=app_context,
            parent=parent
        )
        self.setObjectName("teste03")

        # Inicializa o handler passando o contexto unificado
        self.handler = Teste03
        Handler(self, app_context=app_context)
        self.initialize()

    def setup_ui(self):
        # A inicialização visual básica já é tratada pelo Handler/BaseToolbar
        pass

    def refresh(self):
        self.handler.load_tools_from_json()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    main_window = QtWidgets.QMainWindow()

    # Mock do AppContext para testes isolados
    mock_context = AppContext()
    toolbar = Teste03(app_context=mock_context)

    main_window.addToolBar(toolbar)
    main_window.setWindowTitle("Debug Toolbar: Teste03")
    main_window.resize(400, 100)
    main_window.show()

    sys.exit(app.exec())