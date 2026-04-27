from PySide6 import QtGui, QtCore

class LUTPresets:
    PRESETS = {
        "Grayscale": [(0.0, "#000000"), (1.0, "#FFFFFF")],
        "Inverted": [(0.0, "#FFFFFF"), (1.0, "#000000")],
        "Bone": [(0.0, "#000000"), (0.4, "#966432"), (0.8, "#FFFFE0"), (1.0, "#FFFFFF")],
        "Thermal": [(0.0, "#000000"), (0.33, "#FF0000"), (0.66, "#FFFF00"), (1.0, "#FFFFFF")],
        "Rainbow": [(0.0, "#0000FF"), (0.25, "#00FFFF"), (0.5, "#00FF00"), (0.75, "#FFFF00"), (1.0, "#FF0000")],
        "Blue": [(0.0, "#000000"), (1.0, "#00AAFF")]
    }

    @staticmethod
    def get_lut_icon(name: str, width=180, height=24) -> QtGui.QIcon:
        if name not in LUTPresets.PRESETS:
            return QtGui.QIcon()

        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        gradient = QtGui.QLinearGradient(0, 0, width, 0)
        for pos, color in LUTPresets.PRESETS[name]:
            gradient.setColorAt(pos, QtGui.QColor(color))

        painter.setPen(QtCore.Qt.NoPen)
        painter.fillRect(pixmap.rect(), gradient)
        painter.end()

        return QtGui.QIcon(pixmap)