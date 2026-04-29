from PySide6 import QtWidgets, QtCore
import sys


class TomographyToolbarHandler(QtCore.QObject):
    importDicomRequested = QtCore.Signal()
    validateRequested = QtCore.Signal()
    loadVolumeRequested = QtCore.Signal()
    exportVtiRequested = QtCore.Signal()
    resetViewRequested = QtCore.Signal()

    def __init__(self, toolbar: QtWidgets.QToolBar):
        super().__init__()
        self.toolbar = toolbar
        self._setup_ui()

    def _setup_ui(self):
        first_action = self.toolbar.actions()[0] if self.toolbar.actions() else None
        style_btns = "font-weight: bold; padding: 0px 10px;"

        self.btn_browse = QtWidgets.QPushButton("📁 Open DICOM", self.toolbar)
        self.btn_browse.setStyleSheet(style_btns)
        self.btn_browse.setToolTip("Selecionar pasta contendo fatias DICOM")
        self.toolbar.insertWidget(first_action, self.btn_browse)

        self.btn_validate = QtWidgets.QPushButton("🔍 Validate", self.toolbar)
        self.btn_validate.setStyleSheet(style_btns)
        self.btn_validate.setToolTip("Validar integridade dos arquivos DICOM")
        self.toolbar.insertWidget(first_action, self.btn_validate)

        self.btn_load = QtWidgets.QPushButton("⌛ Load Volume", self.toolbar)
        self.btn_load.setStyleSheet(style_btns)
        self.btn_load.setToolTip("Carregar volume para visualização 3D")
        self.toolbar.insertWidget(first_action, self.btn_load)

        self.btn_export = QtWidgets.QPushButton("💾 Save VTI", self.toolbar)
        self.btn_export.setStyleSheet(style_btns)
        self.btn_export.setToolTip("Persistir volume como arquivo .VTI")
        self.toolbar.insertWidget(first_action, self.btn_export)

        self.btn_reset = QtWidgets.QPushButton("Reset View", self.toolbar)
        self.btn_reset.setStyleSheet(style_btns)
        self.toolbar.insertWidget(first_action, self.btn_reset)

        self.spacer = QtWidgets.QWidget(self.toolbar)
        self.spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.toolbar.insertWidget(first_action, self.spacer)

        self.btn_browse.clicked.connect(self.importDicomRequested.emit)
        self.btn_validate.clicked.connect(self.validateRequested.emit)
        self.btn_load.clicked.connect(self.loadVolumeRequested.emit)
        self.btn_export.clicked.connect(self.exportVtiRequested.emit)
        self.btn_reset.clicked.connect(self.resetViewRequested.emit)

    def set_validation_state(self, validated: bool):
        if validated:
            self.btn_validate.setText("✅ Validated")
            self.btn_validate.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        else:
            self.btn_validate.setText("🔍 Validate")
            self.btn_validate.setStyleSheet("font-weight: bold;")




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Teste Isolado - Tomography Toolbar")
    window.resize(900, 100)

    toolbar = QtWidgets.QToolBar("Tomography Actions")
    window.addToolBar(toolbar)

    handler = TomographyToolbarHandler(toolbar)

    handler.importDicomRequested.connect(lambda: print("Abrir explorador DICOM"))
    handler.validateRequested.connect(lambda: [print("Validando..."), handler.set_validation_state(True)])
    handler.loadVolumeRequested.connect(lambda: print("Iniciando reconstrução de volume"))
    handler.exportVtiRequested.connect(lambda: print("Exportando para projeto/volume.vti"))

    window.show()
    sys.exit(app.exec())