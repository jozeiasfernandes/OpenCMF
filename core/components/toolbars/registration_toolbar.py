from PySide6 import QtWidgets, QtCore, QtGui
from typing import Optional, Any
from core.components.bases.base_toolbar import BaseToolbar
from core.localization.translator import get_base_dir, tr
from core.scene.events.scene_events import SceneEvents, RegistrationEvents


def get_icon(icon_name: str, fallback=QtWidgets.QStyle.StandardPixmap.SP_FileIcon) -> QtGui.QIcon:
    path = get_base_dir() / "appearance" / "icons" / icon_name
    if path.exists():
        return QtGui.QIcon(str(path))
    return QtWidgets.QApplication.style().standardIcon(fallback)


class RegistrationToolbar(BaseToolbar):
    def __init__(self, scene_manager: Any = None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(
            title=tr("toolbar_container.registration.titulo", "Alinhamento de Objetos"),
            scene_manager=scene_manager,
            parent=parent
        )

    def _emit(self, event: str, **payload) -> None:
        if self.has_scene:
            self.scene_manager.events.emit(event, **payload)

    def setup_ui(self):
        # 1. Import Section
        self._add_import_button()
        self.addSeparator()

        # 2. Selection Modes
        self._add_selection_modes()
        self.addSeparator()

        # 3. Actions (Direto na toolbar_container, herdado de QToolBar)
        self.add_tool_button(
            text="",
            callback=lambda: self._emit(RegistrationEvents.REGISTRATION_DELETE_LAST_MARKER),
            icon=get_icon("del_point.svg", QtWidgets.QStyle.StandardPixmap.SP_TrashIcon),
            tooltip=tr("toolbar_container.del_point", "Remover Último Ponto")
        )
        self.add_tool_button(
            text="",
            callback=lambda: self._emit(RegistrationEvents.REGISTRATION_RESET_LAYOUT),
            icon=get_icon("home.svg", QtWidgets.QStyle.StandardPixmap.SP_BrowserReload),
            tooltip=tr("toolbar_container.reset_view", "Resetar Vista")
        )
        self.addSeparator()

        # 4. View Settings
        self.addWidget(QtWidgets.QLabel(tr("toolbar_container.point_size", " Tamanho: ")))
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(5, 50)
        self.slider.setFixedWidth(80)
        self.slider.setValue(20)
        self.slider.valueChanged.connect(
            lambda v: self._emit(RegistrationEvents.REGISTRATION_POINT_SIZE_CHANGED, size=v / 10.0)
        )
        self.addWidget(self.slider)

    def _add_import_button(self):
        btn = self.add_tool_button(
            text="",
            callback=lambda: None,
            icon=get_icon("add.svg", QtWidgets.QStyle.StandardPixmap.SP_FileDialogNewFolder),
            tooltip=tr("toolbar_container.import", "Importar")
        )
        btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        try:
            from core.components.tools.imports.import_objects_panel import ImportObjectsPanel
            self.import_panel = ImportObjectsPanel(self)
            self.import_panel.importRequested.connect(
                lambda cat, sub: self._emit(SceneEvents.REGISTRATION_IMPORT_REQUESTED, category=cat, subcategory=sub)
            )
            btn.clicked.connect(lambda: self.import_panel.show_under(btn))
        except (ImportError, ModuleNotFoundError):
            btn.setEnabled(False)

    def _add_selection_modes(self):
        self.group = QtGui.QActionGroup(self)
        self.group.setExclusive(True)

        actions = [
            (get_icon("cursor.svg", QtWidgets.QStyle.StandardPixmap.SP_ArrowForward), tr("toolbar_container.select", "Seleção"),
             "select"),
            (get_icon("add_point.svg", QtWidgets.QStyle.StandardPixmap.SP_CommandLink),
             tr("toolbar_container.add_point", "Adicionar Pontos"), "add_point")
        ]

        for icon, text, data in actions:
            action = QtGui.QAction(icon, text, self)
            action.setCheckable(True)
            action.setData(data)
            if data == "select": action.setChecked(True)
            self.group.addAction(action)
            self.addAction(action)

        self.group.triggered.connect(lambda a: self._emit(SceneEvents.INTERACTION_MODE_CHANGED, mode=a.data()))

    def _on_mode_changed(self, action: QtGui.QAction):
        self._emit(SceneEvents.INTERACTION_MODE_CHANGED, mode=action.data())

    def _add_action_section(self):
        self.toolbar.addAction(
            get_icon("del_point.svg", QtWidgets.QStyle.StandardPixmap.SP_TrashIcon),
            tr("toolbar_container.del_point", "Remover Último Ponto"),
            lambda: self._emit(RegistrationEvents.REGISTRATION_DELETE_LAST_MARKER)
        )

        self.toolbar.addAction(
            get_icon("home.svg", QtWidgets.QStyle.StandardPixmap.SP_BrowserReload),
            tr("toolbar_container.reset_view", "Resetar Vista"),
            lambda: self._emit(RegistrationEvents.REGISTRATION_RESET_LAYOUT)
        )

    def _add_view_section(self):
        self.toolbar.addWidget(QtWidgets.QLabel(tr("toolbar_container.point_size", " Tamanho: ")))
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(5, 50)
        self.slider.setFixedWidth(80)
        self.slider.setValue(20)
        self.slider.valueChanged.connect(
            lambda v: self._emit(RegistrationEvents.REGISTRATION_POINT_SIZE_CHANGED, size=v / 10.0)
        )
        self.toolbar.addWidget(self.slider)

    def _add_spacer(self):
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    win = QtWidgets.QMainWindow()

    toolbar = RegistrationToolbar(scene_manager=None)
    win.addToolBar(toolbar)

    win.resize(600, 400)
    win.show()

    sys.exit(app.exec())