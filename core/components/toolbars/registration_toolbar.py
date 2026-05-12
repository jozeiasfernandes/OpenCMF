import sys
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore, QtGui

from core.localization.translator import get_base_dir, tr


def get_icon(icon_name: str, fallback=QtWidgets.QStyle.StandardPixmap.SP_FileIcon) -> QtGui.QIcon:
    path = get_base_dir() / "appearance" / "icons" / icon_name
    if path.exists():
        return QtGui.QIcon(str(path))
    return QtWidgets.QApplication.style().standardIcon(fallback)


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
        self.toolbar.setIconSize(QtCore.QSize(20, 20))
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self._add_import_section()
        self.toolbar.addSeparator()
        self._add_action_section()
        self.toolbar.addSeparator()
        self._add_view_section()
        self._add_spacer()

    def _add_import_section(self):
        self.btn_import = QtWidgets.QToolButton()
        self.btn_import.setText(tr("toolbar.import", "Importar"))
        self.btn_import.setIcon(get_icon("add.svg", QtWidgets.QStyle.StandardPixmap.SP_DirIcon))
        self.btn_import.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.toolbar.addWidget(self.btn_import)

        try:
            from core.components.toolbars.imports.import_objects_panel import ImportObjectsPanel
            self.import_panel = ImportObjectsPanel(self.toolbar)
            self.import_panel.importRequested.connect(self.importRequested.emit)
            self.btn_import.clicked.connect(lambda: self.import_panel.show_under(self.btn_import))
        except (ImportError, ModuleNotFoundError):
            self.btn_import.setEnabled(False)

    def _add_action_section(self):
        self.action_del = self.toolbar.addAction(
            get_icon("delete.svg", QtWidgets.QStyle.StandardPixmap.SP_TrashIcon),
            tr("toolbar.del_point", "Remover Ponto")
        )
        self.action_del.triggered.connect(self.deletePointRequested.emit)

        self.action_reset = self.toolbar.addAction(
            get_icon("home.svg", QtWidgets.QStyle.StandardPixmap.SP_BrowserReload),
            tr("toolbar.reset_view", "Resetar Vista")
        )
        self.action_reset.triggered.connect(self.resetLayoutRequested.emit)

    def _add_view_section(self):
        label = QtWidgets.QLabel(tr("toolbar.point_size", " Tamanho: "))
        self.toolbar.addWidget(label)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(5, 50)
        self.slider.setFixedWidth(100)
        self.slider.setValue(20)
        self.slider.valueChanged.connect(lambda v: self.pointSizeChanged.emit(v / 10.0))

        self.toolbar.addWidget(self.slider)

    def _add_spacer(self):
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)


class Component(QtWidgets.QToolBar):
    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle(tr("toolbar.registration.title", "Alinhamento de Objetos"))
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