import sys
from pathlib import Path
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
        self.btn_import = QtWidgets.QPushButton("Import")
        self.toolbar.addWidget(self.btn_import)

        try:
            from core.components.toolbars.imports.import_panel import ImportObjectsPanel
            self.import_panel = ImportObjectsPanel(self.toolbar)
            self.import_panel.importRequested.connect(self.importRequested.emit)
            self.btn_import.clicked.connect(
                lambda: self.import_panel.show_under(self.btn_import)
            )
        except (ImportError, ModuleNotFoundError):
            self.btn_import.setToolTip("Módulo de importação não encontrado")

        self.toolbar.addSeparator()

        self.btn_del_point = QtWidgets.QPushButton("Del Point")
        self.btn_del_point.clicked.connect(self.deletePointRequested.emit)
        self.toolbar.addWidget(self.btn_del_point)

        self.btn_reset = QtWidgets.QPushButton("Reset View")
        self.btn_reset.clicked.connect(self.resetLayoutRequested.emit)
        self.toolbar.addWidget(self.btn_reset)

        self.toolbar.addSeparator()

        self.toolbar.addWidget(QtWidgets.QLabel(" Size: "))
        self.slider_size = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_size.setRange(5, 50)
        self.slider_size.setFixedWidth(80)
        self.slider_size.setValue(20)
        self.slider_size.valueChanged.connect(
            lambda v: self.pointSizeChanged.emit(v / 10.0)
        )
        self.toolbar.addWidget(self.slider_size)


class Component(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alinhar objetos")
        self.setObjectName("registration_toolbar")
        self.handler = RegistrationToolbarHandler(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("OpenCMF - Toolbar Test")
    window.resize(600, 100)

    toolbar = Component()
    window.addToolBar(toolbar)

    # Simulação de conexões
    toolbar.handler.importRequested.connect(
        lambda cat, sub: print(f"Importar: {cat} > {sub}")
    )
    toolbar.handler.pointSizeChanged.connect(
        lambda s: print(f"Novo tamanho: {s}")
    )
    toolbar.handler.deletePointRequested.connect(
        lambda: print("Ponto removido")
    )

    window.show()
    sys.exit(app.exec())