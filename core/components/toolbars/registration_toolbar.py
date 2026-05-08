import sys
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore, QtGui


class RegistrationToolbarHandler(QtCore.QObject):
    importRequested = QtCore.Signal(str, str)
    pointSizeChanged = QtCore.Signal(float)
    deletePointRequested = QtCore.Signal()
    resetLayoutRequested = QtCore.Signal()

    def __init__(self, toolbar: QtWidgets.QToolBar):
        super().__init__()
        self.toolbar = toolbar
        self._setup_ui()

    def _setup_ui(self):
        self._add_import_section()
        self.toolbar.addSeparator()
        self._add_action_section()
        self.toolbar.addSeparator()
        self._add_view_section()
        self._add_spacer()


    def _add_import_section(self):
        self.btn_import = QtWidgets.QPushButton("Import")
        self.toolbar.addWidget(self.btn_import)

        try:
            from core.components.toolbars.imports.import_panel import ImportObjectsPanel
            self.import_panel = ImportObjectsPanel(self.toolbar)
            self.import_panel.importRequested.connect(self.importRequested.emit)
            self.btn_import.clicked.connect(lambda: self.import_panel.show_under(self.btn_import))
        except (ImportError, ModuleNotFoundError):
            self.btn_import.setEnabled(False)

    def _add_action_section(self):
        btn_del = QtWidgets.QPushButton("Del Point")
        btn_del.clicked.connect(self.deletePointRequested.emit)
        self.toolbar.addWidget(btn_del)

        btn_reset = QtWidgets.QPushButton("Reset View")
        btn_reset.clicked.connect(self.resetLayoutRequested.emit)
        self.toolbar.addWidget(btn_reset)

    def _add_view_section(self):
        self.toolbar.addWidget(QtWidgets.QLabel(" Size: "))
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(5, 50)
        slider.setFixedWidth(80)
        slider.setValue(20)
        slider.valueChanged.connect(lambda v: self.pointSizeChanged.emit(v / 10.0))
        self.toolbar.addWidget(slider)

    def _add_spacer(self):
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)


    def _apply_icon(self, button, icon_name, fallback):
        icon_path = Path(__file__).parents[3] / "resources" / "icons" / icon_name
        if icon_path.exists():
            button.setIcon(QtGui.QIcon(str(icon_path)))
        else:
            button.setIcon(button.style().standardIcon(fallback))


class Component(QtWidgets.QToolBar):
    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle("Alinhar objetos")
        self.setObjectName("registration_toolbar")
        self.__module_path__ = Path(__file__).resolve()
        self.handler = RegistrationToolbarHandler(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = QtWidgets.QMainWindow()
    win.addToolBar(Component())
    win.show()
    sys.exit(app.exec())