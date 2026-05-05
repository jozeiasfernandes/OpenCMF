import sys
from PySide6 import QtWidgets, QtCore
from pathlib import Path
from core.components.toolbars.imports.import_panel import ImportObjectsPanel


class Component(QtWidgets.QToolBar):
    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle("Alinhar objetos")
        self.__module_path__ = Path(__file__).resolve()
        self.handler = RegistrationToolbarHandler(self)

class RegistrationToolbarHandler(QtCore.QObject):
    importRequested = QtCore.Signal(str)
    addPointToggled = QtCore.Signal(bool)
    deletePointRequested = QtCore.Signal()
    pointSizeChanged = QtCore.Signal(float)
    resetLayoutRequested = QtCore.Signal()

    def __init__(self, toolbar: QtWidgets.QToolBar):
        super().__init__()
        self.toolbar = toolbar
        self._setup_ui()

    def _setup_ui(self):
        style_btns = """
            QPushButton { 
                font-weight: bold;
                padding: 4px 12px;
                margin: 2px;
                background-color: #333;
                color: white;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #444; }
            QPushButton:checked { background-color: #0078d7; }
        """

        # IMPORT
        self.btn_import = QtWidgets.QPushButton("Import Objects")
        self.btn_import.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_import)

        self.import_panel = ImportObjectsPanel(self.toolbar)
        self.import_panel.importRequested.connect(self.importRequested.emit)

        self.btn_import.clicked.connect(self._toggle_import_panel)

        self.toolbar.addSeparator()

        # POINTS
        self.btn_add = QtWidgets.QPushButton("Add Point")
        self.btn_add.setCheckable(True)
        self.btn_add.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_add)

        self.btn_del = QtWidgets.QPushButton("Delete Point")
        self.btn_del.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_del)

        self.toolbar.addSeparator()

        # VIEW
        self.btn_reset = QtWidgets.QPushButton("Reset View")
        self.btn_reset.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_reset)

        self.toolbar.addSeparator()

        # SIZE CONTROL
        self.toolbar.addWidget(QtWidgets.QLabel(" SIZE: "))

        self.slider_size = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_size.setRange(5, 50)
        self.slider_size.setValue(15)
        self.slider_size.setFixedWidth(80)
        self.toolbar.addWidget(self.slider_size)

        # SIGNALS
        self.btn_add.toggled.connect(self.addPointToggled.emit)
        self.btn_del.clicked.connect(self.deletePointRequested.emit)
        self.btn_reset.clicked.connect(self.resetLayoutRequested.emit)
        self.slider_size.valueChanged.connect(lambda v: self.pointSizeChanged.emit(v / 10.0))

    def _toggle_import_panel(self):
        if self.import_panel.isVisible():
            self.import_panel.hide()
        else:
            self.import_panel.show_under(self.btn_import)


if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Test - Registration Toolbar")
    window.resize(800, 200)

    toolbar = QtWidgets.QToolBar()
    window.addToolBar(toolbar)

    handler = RegistrationToolbarHandler(toolbar)

    handler.importRequested.connect(lambda x: print("Import requested:", x))
    handler.addPointToggled.connect(lambda v: print("Add Point:", v))
    handler.deletePointRequested.connect(lambda: print("Delete Point"))
    handler.pointSizeChanged.connect(lambda v: print("Point Size:", v))
    handler.resetLayoutRequested.connect(lambda: print("Reset View"))

    window.show()
    sys.exit(app.exec())