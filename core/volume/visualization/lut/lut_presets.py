from PySide6 import QtGui, QtCore


class LUTPresets:
    PRESETS = {
        # Essenciais
        "Grayscale": [(0.0, "#000000"), (1.0, "#FFFFFF")],
        "Inverted": [(0.0, "#FFFFFF"), (1.0, "#000000")],

        # Especializados para CMF (Osso e Tecidos)
        "Bone": [(0.0, "#000000"), (0.4, "#966432"), (0.8, "#FFFFE0"), (1.0, "#FFFFFF")],
        "VR Bones": [(0.0, "#000000"), (0.1, "#3c2d00"), (0.5, "#ffdc46"), (1.0, "#ffffc8")],
        "Hot Iron": [(0.0, "#000000"), (0.25, "#800000"), (0.5, "#ff8000"), (0.75, "#ffff80"), (1.0, "#ffffff")],
        "Cardiac": [(0.0, "#000000"), (0.25, "#0000ff"), (0.5, "#ff0000"), (0.75, "#ffff00"), (1.0, "#ffffff")],

        # Análise de Densidade/Fluxo
        "GE Color": [(0.0, "#000000"), (0.2, "#005a5a"), (0.4, "#00ffff"), (0.6, "#ff00ff"), (0.8, "#ffff00"),
                     (1.0, "#ffffff")],
        "Thermal": [(0.0, "#000000"), (0.33, "#FF0000"), (0.66, "#FFFF00"), (1.0, "#FFFFFF")],
        "Rainbow": [(0.0, "#0000FF"), (0.25, "#00FFFF"), (0.5, "#00FF00"), (0.75, "#FFFF00"), (1.0, "#FF0000")],
        "Jet": [(0.0, "#00007f"), (0.25, "#00ffff"), (0.5, "#7fff7f"), (0.75, "#ffff00"), (1.0, "#7f0000")],

        # Filtros de realce
        "Ice": [(0.0, "#000000"), (0.5, "#00ffff"), (1.0, "#ffffff")],
        "Ired": [(0.0, "#000000"), (0.5, "#ffaaaa"), (1.0, "#ffffff")],
    }

    @staticmethod
    def get_lut_icon(name: str, width=100, height=18) -> QtGui.QIcon:
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
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawRoundedRect(0, 0, width, height, 3, 3)
        painter.end()

        return QtGui.QIcon(pixmap)