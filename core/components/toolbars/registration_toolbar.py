import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from PySide6 import QtWidgets, QtCore, QtGui

from core.localization.translator import get_base_dir, tr
from core.scene.events.scene_events import (
    REGISTRATION_DELETE_LAST_MARKER,
    REGISTRATION_IMPORT_REQUESTED,
    REGISTRATION_POINT_SIZE_CHANGED,
    REGISTRATION_RESET_LAYOUT,
    INTERACTION_MODE_CHANGED
)

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager


def get_icon(icon_name: str, fallback=QtWidgets.QStyle.StandardPixmap.SP_FileIcon) -> QtGui.QIcon:
    path = get_base_dir() / "appearance" / "icons" / icon_name
    if path.exists():
        return QtGui.QIcon(str(path))
    return QtWidgets.QApplication.style().standardIcon(fallback)


class RegistrationToolbarHandler(QtCore.QObject):
    def __init__(self, toolbar: QtWidgets.QToolBar, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.toolbar = toolbar
        self._scene_manager = scene_manager
        self._setup_ui()

    def _emit(self, event: str, **payload) -> None:
        if self._scene_manager:
            self._scene_manager.events.emit(event, **payload)

    def _setup_ui(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)

        self._add_import_section()
        self.toolbar.addSeparator()
        self._add_selection_modes()
        self.toolbar.addSeparator()
        self._add_action_section()
        self.toolbar.addSeparator()
        self._add_view_section()
        self._add_spacer()

    def _add_import_section(self):
        self.btn_import = QtWidgets.QToolButton()
        self.btn_import.setIcon(get_icon("add.svg", QtWidgets.QStyle.StandardPixmap.SP_FileDialogNewFolder))
        self.btn_import.setToolTip(tr("toolbar.import", "Importar"))
        self.btn_import.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.toolbar.addWidget(self.btn_import)

        try:
            from core.components.tools.imports.import_objects_panel import ImportObjectsPanel
            self.import_panel = ImportObjectsPanel(self.toolbar)
            self.import_panel.importRequested.connect(
                lambda cat, sub: self._emit(REGISTRATION_IMPORT_REQUESTED, category=cat, subcategory=sub)
            )
            self.btn_import.clicked.connect(lambda: self.import_panel.show_under(self.btn_import))
        except (ImportError, ModuleNotFoundError):
            self.btn_import.setEnabled(False)

    def _add_selection_modes(self):
        self.group = QtGui.QActionGroup(self)
        self.group.setExclusive(True)

        self.action_select = QtGui.QAction(
            get_icon("cursor.svg", QtWidgets.QStyle.StandardPixmap.SP_ArrowForward),
            tr("toolbar.select", "Seleção"), self
        )
        self.action_select.setCheckable(True)
        self.action_select.setChecked(True)
        self.action_select.setData("select")

        self.action_add_point = QtGui.QAction(
            get_icon("add_point.svg", QtWidgets.QStyle.StandardPixmap.SP_CommandLink),
            tr("toolbar.add_point", "Adicionar Pontos"), self
        )
        self.action_add_point.setCheckable(True)
        self.action_add_point.setData("add_point")

        self.group.addAction(self.action_select)
        self.group.addAction(self.action_add_point)

        self.toolbar.addAction(self.action_select)
        self.toolbar.addAction(self.action_add_point)

        self.group.triggered.connect(self._on_mode_changed)

    def _on_mode_changed(self, action: QtGui.QAction):
        self._emit(INTERACTION_MODE_CHANGED, mode=action.data())

    def _add_action_section(self):
        self.toolbar.addAction(
            get_icon("del_point.svg", QtWidgets.QStyle.StandardPixmap.SP_TrashIcon),
            tr("toolbar.del_point", "Remover Último Ponto"),
            lambda: self._emit(REGISTRATION_DELETE_LAST_MARKER)
        )

        self.toolbar.addAction(
            get_icon("home.svg", QtWidgets.QStyle.StandardPixmap.SP_BrowserReload),
            tr("toolbar.reset_view", "Resetar Vista"),
            lambda: self._emit(REGISTRATION_RESET_LAYOUT)
        )

    def _add_view_section(self):
        self.toolbar.addWidget(QtWidgets.QLabel(tr("toolbar.point_size", " Tamanho: ")))
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(5, 50)
        self.slider.setFixedWidth(80)
        self.slider.setValue(20)
        self.slider.valueChanged.connect(
            lambda v: self._emit(REGISTRATION_POINT_SIZE_CHANGED, size=v / 10.0)
        )
        self.toolbar.addWidget(self.slider)

    def _add_spacer(self):
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)


class Component(QtWidgets.QToolBar):
    def __init__(self, modulo=None, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle(tr("toolbar.registration.title", "Alinhamento de Objetos"))
        self.setObjectName("registration_toolbar")
        self.handler = RegistrationToolbarHandler(self, scene_manager=scene_manager)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = QtWidgets.QMainWindow()
    win.addToolBar(Component())
    win.show()
    sys.exit(app.exec())