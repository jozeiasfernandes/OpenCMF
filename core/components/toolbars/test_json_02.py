from typing import Optional, TYPE_CHECKING
import json
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.localization.translator import tr

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager


class Test_json_02Handler(QtCore.QObject):
    def __init__(self, toolbar: QtWidgets.QToolBar, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.toolbar = toolbar
        self._scene_manager = scene_manager
        self.json_path = Path(__file__).with_suffix(".json")
        self._setup_ui()

    def _setup_ui(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        self.load_tools_from_json()

    def load_tools_from_json(self):
        self.toolbar.clear()
        self.toolbar.addWidget(QtWidgets.QLabel("test_json_02"))

        if not self.json_path.exists():
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                tool_paths = json.load(f)

            for path_str in tool_paths:
                path = Path(path_str)
                if path.exists():
                    pass
        except Exception as e:
            print(f"Erro ao carregar ferramentas: {e}")


class Component(QtWidgets.QToolBar):
    toolbar_name = "test_json_02"

    def __init__(self, modulo=None, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle(self.toolbar_name)
        self.setObjectName("test_json_02")
        self.handler = Test_json_02Handler(self, scene_manager=scene_manager)

    def refresh(self):
        self.handler.load_tools_from_json()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main_window = QtWidgets.QMainWindow()
    toolbar = Component()
    main_window.addToolBar(toolbar)

    main_window.setWindowTitle("Debug Toolbar: test_json_02")
    main_window.resize(400, 100)
    main_window.show()

    sys.exit(app.exec())