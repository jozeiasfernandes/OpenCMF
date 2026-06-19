import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PySide6 import QtWidgets, QtCore, QtGui

from core.localization.translator import get_base_dir, tr
from core.tools.base.base_tool import BaseTool

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager


def get_icon(icon_name: str, fallback=QtWidgets.QStyle.StandardPixmap.SP_FileIcon) -> QtGui.QIcon:
    path = get_base_dir() / "appearance" / "icons" / icon_name
    if path.exists():
        return QtGui.QIcon(str(path))
    return QtWidgets.QApplication.style().standardIcon(fallback)


class TestToolbarHandler(QtCore.QObject):
    def __init__(self, toolbar: QtWidgets.QToolBar, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.toolbar = toolbar
        self._scene_manager = scene_manager
        self._setup_ui()

    def _setup_ui(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self._add_spacer()

    def _add_spacer(self):
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)


class TestToolbar(QtWidgets.QToolBar):
    def __init__(self, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.setWindowTitle("Test Toolbar - Vazia")
        self.setObjectName("test_toolbar_empty")
        self.handler = TestToolbarHandler(self, scene_manager=scene_manager)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("Teste de Toolbar Vazia")
    win.resize(900, 600)

    toolbar = TestToolbar()
    win.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)

    win.show()
    sys.exit(app.exec())