from typing import Optional, TYPE_CHECKING
import json
import importlib.util
import inspect
import logging
import traceback
from pathlib import Path

from PySide6 import QtWidgets, QtCore, QtGui
from core.components.bases.base_tool import BaseTool
from core.components.bases.base_tool import ToolManager

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager

logger = logging.getLogger("ToolbarLoader")


class BaseToolbar(QtWidgets.QToolBar):
    """Classe base_tool unificada para toolbars com suporte a injeção de dependência."""

    def __init__(self, title: str, tool_manager: ToolManager, scene_manager: Optional["SceneManager"] = None,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(title, parent)
        self.tool_manager = tool_manager
        self.scene_manager = scene_manager
        self.setObjectName(title.lower().replace(" ", "_"))
        self.setIconSize(QtCore.QSize(24, 24))

    def add_tool_button(self, text: str, callback, icon: Optional[QtGui.QIcon] = None, tooltip: str = ""):
        btn = QtWidgets.QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        if icon: btn.setIcon(icon)
        btn.clicked.connect(callback)
        self.addWidget(btn)
        return btn


class Teste02Toolbar(BaseToolbar):
    """Implementação específica que carrega ferramentas via JSON."""

    def __init__(self, tool_manager, scene_manager=None):
        super().__init__("Teste02", tool_manager, scene_manager)
        self.json_path = Path(__file__).resolve().with_suffix(".json")
        self.refresh()

    def refresh(self):
        self.clear()
        if not self.json_path.exists():
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                tool_paths = json.load(f)

            for path_str in tool_paths:
                self._load_tool(path_str)
        except Exception as e:
            logger.error(f"Erro ao processar JSON: {e}")

    def _load_tool(self, path_str: str):
        root_path = Path("C:/OpenCMF")
        path = root_path / "core" / "components" / "tools" / Path(path_str).name

        if not path.exists():
            return

        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj is not BaseTool:
                    # Instancia a ferramenta
                    instance = obj()

                    # Cria o botão que chama o ToolManager para ativar a instância
                    def create_callback(tool_instance):
                        return lambda: self.tool_manager.activate_tool(tool_instance)

                    btn = instance.create_button(create_callback(instance))
                    self.addWidget(btn)
        except Exception:
            logger.error(f"Falha ao carregar {path}:\n{traceback.format_exc()}")


if __name__ == "__main__":
    import sys
    from core.components.bases.base_tool import ToolManager

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()

    tool_manager = ToolManager(context=main_window)
    toolbar = Teste02Toolbar(tool_manager=tool_manager)

    main_window.addToolBar(toolbar)
    main_window.setWindowTitle("Debug Toolbar: Teste02")
    main_window.resize(400, 100)
    main_window.show()

    sys.exit(app.exec())