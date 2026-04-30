from PySide6 import QtWidgets, QtCore
import sys


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

        self.btn_import = QtWidgets.QPushButton("Import Objects")
        self.btn_import.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_import)

        self.btn_add = QtWidgets.QPushButton("Add Point")
        self.btn_add.setCheckable(True)
        self.btn_add.setStyleSheet(style_btns)
        self.btn_add.setToolTip("Add Landmark (A)")
        self.toolbar.addWidget(self.btn_add)

        self.btn_del = QtWidgets.QPushButton("Delete Point")
        self.btn_del.setStyleSheet(style_btns)
        self.btn_del.setToolTip("Delete Last Point (Z)")
        self.toolbar.addWidget(self.btn_del)

        self.btn_reset = QtWidgets.QPushButton("Reset View")
        self.btn_reset.setStyleSheet(style_btns)
        self.btn_reset.setToolTip("Restaurar layout de duas janelas 3D")
        self.toolbar.addWidget(self.btn_reset)

        self.toolbar.addSeparator()

        label_size = QtWidgets.QLabel(" POINT SIZE: ")
        label_size.setStyleSheet("font-size: 10px; font-weight: bold; margin-left: 10px;")
        self.toolbar.addWidget(label_size)

        self.slider_size = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_size.setMinimum(5)
        self.slider_size.setMaximum(50)
        self.slider_size.setValue(15)
        self.slider_size.setFixedWidth(80)
        self.toolbar.addWidget(self.slider_size)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)

        self.btn_import.clicked.connect(self.importRequested.emit)
        self.btn_add.toggled.connect(self.addPointToggled.emit)
        self.btn_del.clicked.connect(self.deletePointRequested.emit)
        self.btn_reset.clicked.connect(self.resetLayoutRequested.emit)
        self.slider_size.valueChanged.connect(self._on_slider_changed)

    def _on_slider_changed(self, value):
        self.pointSizeChanged.emit(value / 10.0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Teste Isolado Toolbar")
    window.resize(900, 100)

    toolbar = QtWidgets.QToolBar("Registration Toolbar")
    toolbar.setMovable(False)
    window.addToolBar(toolbar)

    handler = RegistrationToolbarHandler(toolbar)

    handler.importRequested.connect(lambda: print("Import solicitado"))
    handler.addPointToggled.connect(lambda state: print(f"Add Point: {state}"))
    handler.deletePointRequested.connect(lambda: print("Delete solicitado"))
    handler.resetLayoutRequested.connect(lambda: print("Reset Layout solicitado"))
    handler.pointSizeChanged.connect(lambda size: print(f"Tamanho do ponto: {size}"))

    window.show()
    sys.exit(app.exec())