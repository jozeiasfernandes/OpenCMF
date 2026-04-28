from PySide6 import QtWidgets, QtCore

class RegistrationToolbarHandler(QtCore.QObject):
    importRequested = QtCore.Signal()
    addPointToggled = QtCore.Signal(bool)
    deletePointRequested = QtCore.Signal()
    pointSizeChanged = QtCore.Signal(float)
    resetLayoutRequested = QtCore.Signal()

    def __init__(self, toolbar: QtWidgets.QToolBar):
        super().__init__()
        self.toolbar = toolbar
        self._setup_ui()

    def _setup_ui(self):
        first_action = self.toolbar.actions()[0] if self.toolbar.actions() else None
        style_btns = "font-weight: bold; padding: 0px 10px;"

        self.btn_import = QtWidgets.QPushButton("Import Objects", self.toolbar)
        self.btn_import.setStyleSheet(style_btns)
        self.toolbar.insertWidget(first_action, self.btn_import)

        self.btn_add = QtWidgets.QPushButton("Add Point", self.toolbar)
        self.btn_add.setCheckable(True)
        self.btn_add.setStyleSheet(style_btns)
        self.btn_add.setToolTip("Add Landmark (A)")
        self.toolbar.insertWidget(first_action, self.btn_add)

        self.btn_del = QtWidgets.QPushButton("Delete Point", self.toolbar)
        self.btn_del.setStyleSheet(style_btns)
        self.btn_del.setToolTip("Delete Last Point (Z)")
        self.toolbar.insertWidget(first_action, self.btn_del)

        self.btn_reset = QtWidgets.QPushButton("Reset View", self.toolbar)
        self.btn_reset.setStyleSheet(style_btns)
        self.btn_reset.setToolTip("Restaurar layout de duas janelas 3D")
        self.toolbar.insertWidget(first_action, self.btn_reset)

        label_size = QtWidgets.QLabel("  POINT SIZE: ", self.toolbar)
        label_size.setStyleSheet("font-size: 10px; font-weight: bold;")
        self.toolbar.insertWidget(first_action, label_size)

        self.slider_size = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.toolbar)
        self.slider_size.setMinimum(5)
        self.slider_size.setMaximum(50)
        self.slider_size.setValue(15)
        self.slider_size.setFixedWidth(80)
        self.toolbar.insertWidget(first_action, self.slider_size)

        self.spacer = QtWidgets.QWidget(self.toolbar)
        self.spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.toolbar.insertWidget(first_action, self.spacer)

        self.btn_import.clicked.connect(self.importRequested.emit)
        self.btn_add.toggled.connect(self.addPointToggled.emit)
        self.btn_del.clicked.connect(self.deletePointRequested.emit)
        self.btn_reset.clicked.connect(self.resetLayoutRequested.emit)
        self.slider_size.valueChanged.connect(self._on_slider_changed)

    def _on_slider_changed(self, value):
        self.pointSizeChanged.emit(value / 10.0)