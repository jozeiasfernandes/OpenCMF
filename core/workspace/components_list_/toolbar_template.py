from typing import Optional, TYPE_CHECKING
from PySide6 import QtWidgets, QtCore
from core.localization.translator import tr

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager

class {class_name}Handler(QtCore.QObject):
    def __init__(self, toolbar: QtWidgets.QToolBar, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.toolbar = toolbar
        self._scene_manager = scene_manager
        self._setup_ui()

    def _setup_ui(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        self.toolbar.addWidget(QtWidgets.QLabel("{name}"))

class Component(QtWidgets.QToolBar):
    toolbar_name = "{name}"

    def __init__(self, modulo=None, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle(self.toolbar_name)
        self.setObjectName("{object_name}")
        self.handler = {class_name}Handler(self, scene_manager=scene_manager)