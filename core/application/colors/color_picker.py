from PySide6 import QtWidgets, QtCore, QtGui
from .hue_bar import HueBar
from .sat_val_canvas import SatValCanvas
from .color_utils import hsv_to_rgb

class ColorPickerWidget(QtWidgets.QWidget):
    colorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = SatValCanvas()
        self.hue_bar = HueBar()

        layout.addWidget(self.canvas)
        layout.addWidget(self.hue_bar)

        self.hue_bar.hueChanged.connect(self._on_hue_changed)
        self.canvas.colorPicked.connect(self._on_sat_val_changed)

    def _on_hue_changed(self, hue):
        self.canvas.set_hue(hue)
        self._update_color()

    def _on_sat_val_changed(self, sat, val):
        self._update_color()

    def _update_color(self):
        h = self.hue_bar.get_hue()
        s = self.canvas.get_sat()
        v = self.canvas.get_val()
        r, g, b = hsv_to_rgb(h, s, v)
        color = QtGui.QColor.fromRgbF(r, g, b)
        self.colorChanged.emit(color)

    def set_rgb(self, rgb):
        color = QtGui.QColor.fromRgbF(*rgb)
        self.hue_bar.set_hue(color.hueF() * 360)
        self.canvas.set_sat_val(color.saturationF(), color.valueF())