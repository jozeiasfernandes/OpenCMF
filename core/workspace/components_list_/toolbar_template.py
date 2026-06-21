from typing import Optional, TYPE_CHECKING
import json
import importlib.util
import inspect
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.localization.translator import tr
from core.components.tools.base.base_tool import BaseTool
from core.components.tools.base.base_toolbar_handler import BaseToolbarHandler

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager


class {class_name}Handler(BaseToolbarHandler):
    def __init__(self, toolbar: QtWidgets.QToolBar, scene_manager: Optional["SceneManager"] = None):
        super().__init__(toolbar, context=None)
        self.toolbar = toolbar
        self._scene_manager = scene_manager

        self.json_path = Path(__file__).resolve().with_suffix(".json")

        print(f"DEBUG: O Handler está procurando o JSON em: {self.json_path}")

        self._setup_ui()

    def _setup_ui(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        self.load_tools_from_json()

    def load_tools_from_json(self) -> None:
        """Carrega as ferramentas salvas no JSON e registra no toolbar."""
        self.clear_toolbar()

        if not self.json_path.exists():
            print(f"DEBUG: JSON não encontrado em: {self.json_path}")
            return

        print(f"DEBUG: Carregando ferramentas de: {self.json_path}")

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                tool_paths: list[str] = json.load(f)
        except Exception as e:
            print(f"ERRO ao ler JSON {self.json_path}: {e}")
            return

        components_root = self.components_path  # Usa a referência já existente (melhor prática)

        loaded_count = 0
        for path_str in tool_paths:
            if not path_str:
                continue

            full_path: Path = None  # type: ignore

            try:
                candidate = Path(path_str)

                # 1ª tentativa: caminho relativo ao components_path (padrão do save)
                if not candidate.is_absolute():
                    full_path = (components_root / candidate).resolve()
                else:
                    full_path = candidate.resolve()

                # 2ª tentativa: fallback por nome (caso o caminho tenha mudado)
                if not full_path.exists():
                    full_path = (components_root / candidate.name).resolve()

                # 3ª tentativa: busca mais profunda (opcional)
                if not full_path.exists():
                    full_path = (components_root / "tools" / candidate.name).resolve()

                if full_path.exists():
                    tool_instance = self._instanciar_tool(full_path)
                    if tool_instance:
                        self.register_tool(tool_instance)
                        loaded_count += 1
                    else:
                        print(f"AVISO: Falha ao instanciar ferramenta: {full_path.name}")
                else:
                    print(f"AVISO: Arquivo não encontrado: {full_path}")

            except Exception as e:
                print(f"ERRO ao processar caminho '{path_str}': {e}")

        print(f"DEBUG: Carregamento concluído. {loaded_count} ferramenta(s) carregada(s).")

    def _instanciar_tool(self, path: Path) -> Optional[BaseTool]:
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj is not BaseTool:
                    return obj()
        except Exception as e:
            print(f"Falha ao instanciar {path}: {e}")

        return None


class Component(QtWidgets.QToolBar):
    toolbar_name = "{name}"

    def __init__(self, modulo=None, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle(self.toolbar_name)
        self.setObjectName("{object_name}")
        self.handler = {class_name}Handler(self, scene_manager=scene_manager)

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