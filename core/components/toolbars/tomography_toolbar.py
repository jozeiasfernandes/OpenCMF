import sys
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

try:
    from core.volume.lookup_table.lut_presets import LUTPresets
except ImportError:
    class LUTPresets:
        PRESETS = {
            "Grayscale": [(0.0, "#000000"), (1.0, "#FFFFFF")],
            "Inverted": [(0.0, "#FFFFFF"), (1.0, "#000000")],
            "Bone": [(0.0, "#000000"), (0.4, "#966432"), (0.8, "#FFFFE0"), (1.0, "#FFFFFF")],
            "Thermal": [(0.0, "#000000"), (0.33, "#FF0000"), (0.66, "#FFFF00"), (1.0, "#FFFFFF")],
            "Rainbow": [(0.0, "#0000FF"), (0.25, "#00FFFF"), (0.5, "#00FF00"), (0.75, "#FFFF00"), (1.0, "#FF0000")],
            "Blue": [(0.0, "#000000"), (1.0, "#00AAFF")]
        }


class LUTDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        name = index.data()
        stops = LUTPresets.PRESETS.get(name, [])
        rect = option.rect

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(rect, option.palette.highlight())

        gradient = QtGui.QLinearGradient(rect.left() + 5, 0, rect.right() - 5, 0)
        for pos, hex_val in stops:
            gradient.setColorAt(pos, QtGui.QColor(hex_val))

        grad_rect = rect.adjusted(5, 4, -5, -4)
        painter.setBrush(gradient)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(grad_rect, 3, 3)

        font = painter.font()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)

        painter.setPen(QtGui.QColor(0, 0, 0, 200))
        painter.drawText(rect.adjusted(1, 1, 1, 1), QtCore.Qt.AlignCenter, name)
        painter.setPen(QtCore.Qt.white)
        painter.drawText(rect, QtCore.Qt.AlignCenter, name)

        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(100, 30)


class TomographyToolbarHandler(QtCore.QObject):
    importDicomRequested = QtCore.Signal()
    validateRequested = QtCore.Signal()
    loadVolumeRequested = QtCore.Signal()
    exportVtiRequested = QtCore.Signal()
    resetViewRequested = QtCore.Signal()
    layoutChanged = QtCore.Signal(str)
    colorMapChanged = QtCore.Signal(str)

    def __init__(self, toolbar: QtWidgets.QToolBar):
        super().__init__()
        self.toolbar = toolbar
        self._setup_ui()

    def _setup_ui(self):
        self.toolbar.setFixedHeight(43)
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("""
            QToolBar { 
                background: #1E1E1E; 
                border-bottom: 1px solid #333; 
                spacing: 10px; 
                padding: 0px 10px; 
            } 
            QPushButton {
                background: #333;
                color: white;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 2px 8px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background: #444; }
            QPushButton:pressed { background: #222; }
            QComboBox { 
                background: #333; 
                color: white; 
                border: 1px solid #444; 
                border-radius: 3px;
                padding: 2px 5px; 
                min-width: 120px; 
            }
            QComboBox::drop-down { border: none; }
            QLabel { 
                color: #888; 
                font-size: 10px; 
                font-weight: bold; 
                text-transforms: uppercase;
                margin-left: 5px;
            }
        """)

        self.btn_browse = QtWidgets.QPushButton("📁 Open DICOM")
        self.toolbar.addWidget(self.btn_browse)

        self.btn_validate = QtWidgets.QPushButton("🔍 Validate")
        self.toolbar.addWidget(self.btn_validate)

        self.btn_load = QtWidgets.QPushButton("⌛ Load Volume")
        self.toolbar.addWidget(self.btn_load)

        self.btn_export = QtWidgets.QPushButton("💾 Save VTI")
        self.toolbar.addWidget(self.btn_export)

        self.btn_reset = QtWidgets.QPushButton("🔄 Reset")
        self.toolbar.addWidget(self.btn_reset)

        self.toolbar.addSeparator()

        self.toolbar.addWidget(QtWidgets.QLabel("Layout"))
        self.combo_layout = QtWidgets.QComboBox()
        self.combo_layout.addItems(["4 Quadrantes", "3D Destacado", "Apenas 3D", "Axial", "Sagital", "Coronal"])
        self.toolbar.addWidget(self.combo_layout)

        self.toolbar.addWidget(QtWidgets.QLabel("Color Map"))
        self.combo_color = QtWidgets.QComboBox()
        self.combo_color.setItemDelegate(LUTDelegate(self.combo_color))
        self.combo_color.addItems(list(LUTPresets.PRESETS.keys()))
        self.toolbar.addWidget(self.combo_color)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)

        self.btn_browse.clicked.connect(self.importDicomRequested.emit)
        self.btn_validate.clicked.connect(self.validateRequested.emit)
        self.btn_load.clicked.connect(self.loadVolumeRequested.emit)
        self.btn_export.clicked.connect(self.exportVtiRequested.emit)
        self.btn_reset.clicked.connect(self.resetViewRequested.emit)
        self.combo_layout.currentTextChanged.connect(self.layoutChanged.emit)
        self.combo_color.currentTextChanged.connect(self.colorMapChanged.emit)

    def set_validation_state(self, validated: bool):
        if validated:
            self.btn_validate.setText("Validated")
            self.btn_validate.setStyleSheet("background-color: #27ae60; color: white; border: 1px solid #2ecc71;")
        else:
            self.btn_validate.setText("Validate")
            self.btn_validate.setStyleSheet("")


class Component(QtWidgets.QToolBar):
    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle("Tomografia")
        self.__module_path__ = Path(__file__).resolve()
        self.handler = TomographyToolbarHandler(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Teste Toolbar Tomografia")
    window.resize(1100, 100)

    toolbar_comp = Component()
    window.addToolBar(toolbar_comp)

    toolbar_comp.handler.colorMapChanged.connect(lambda lut: print(f"LUT alterada para: {lut}"))

    window.show()
    sys.exit(app.exec())