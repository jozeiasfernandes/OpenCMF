from PySide6 import QtCore, QtGui


class ColorManager(QtCore.QObject):
    colorChanged = QtCore.Signal(str, QtGui.QColor)

    def __init__(self):
        super().__init__()

        self._colors = {
            "background": QtGui.QColor("#1E1E1E"),
            "bone": QtGui.QColor("#E8D9C5"),
            "soft_tissue": QtGui.QColor("#D19A8A"),
            "implant": QtGui.QColor("#C0C0C0"),
            "selection": QtGui.QColor("#3EA6FA"),
        }

    def set_color(self, key: str, color: QtGui.QColor):
        self._colors[key] = color
        self.colorChanged.emit(key, color)

    def get_color(self, key: str) -> QtGui.QColor:
        return self._colors.get(key, QtGui.QColor("white"))

    def get_rgbf(self, key: str):
        c = self.get_color(key)
        return c.redF(), c.greenF(), c.blueF()