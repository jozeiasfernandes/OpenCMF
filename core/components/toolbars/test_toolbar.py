import sys
from typing import TYPE_CHECKING, Optional
from PySide6 import QtWidgets, QtCore

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager


class TestToolbarHandler(QtCore.QObject):
    def __init__(self, parent_widget: QtWidgets.QWidget, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.widget = parent_widget
        self.layout = parent_widget.layout()
        self._scene_manager = scene_manager
        self._setup_ui()

    def _setup_ui(self):
        self.widget.setFixedHeight(40)
        self._add_spacer()

    def _add_spacer(self):
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.layout.addWidget(spacer)


class TestToolbar(QtWidgets.QWidget):
    def __init__(self, modulo=None, scene_manager: Optional["SceneManager"] = None, parent=None):
        super().__init__(parent)
        self.modulo = modulo
        self.setObjectName("test_toolbar_widget")

        # O atributo WA_StyledBackground permite que o widget aceite background via QSS
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
            #test_toolbar_widget {
                background-color: #3c8033;
                border: 1px solid #000;
            }
        """)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.handler = TestToolbarHandler(self, scene_manager=scene_manager)


class Component(TestToolbar):
    def __init__(self, modulo=None, scene_manager: Optional["SceneManager"] = None):
        super().__init__(modulo=modulo, scene_manager=scene_manager)
        self.nome = "Test Toolbar"


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("Teste de Toolbar Integrada")
    win.resize(900, 600)

    toolbar = Component()

    central = QtWidgets.QWidget()
    layout_win = QtWidgets.QVBoxLayout(central)
    layout_win.addWidget(toolbar)
    layout_win.addStretch()

    win.setCentralWidget(central)
    win.show()
    sys.exit(app.exec())