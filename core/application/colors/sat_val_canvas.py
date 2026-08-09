"""
core.colors.sat_val_canvas
=========================
Canvas 2-D interativo: eixo X = saturação, eixo Y = valor (brilho).
Emite colorPicked(sat: float, val: float) ambos em [0, 1].
"""

from PySide6 import QtWidgets, QtCore, QtGui
from .color_utils import hsv_to_rgb


class SatValCanvas(QtWidgets.QWidget):
    colorPicked = QtCore.Signal(float, float)   # sat, val ∈ [0, 1]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 140)
        self.setCursor(QtCore.Qt.CrossCursor)
        self._hue_deg: float = 0.0
        self._sat: float = 1.0
        self._val: float = 1.0
        self._canvas: QtGui.QPixmap | None = None

    # ── rendering ─────────────────────────────────────────────────────────────

    def _build_canvas(self) -> None:
        w, h = self.width(), self.height()
        img = QtGui.QImage(w, h, QtGui.QImage.Format_RGB32)
        hue = self._hue_deg
        for x in range(w):
            sat = x / w
            for y in range(h):
                val = 1.0 - (y / h)
                r, g, b = hsv_to_rgb(hue, sat, val)
                img.setPixelColor(x, y, QtGui.QColor(
                    int(r * 255), int(g * 255), int(b * 255)))
        self._canvas = QtGui.QPixmap.fromImage(img)

    def paintEvent(self, _event) -> None:
        if self._canvas is None or self._canvas.width() != self.width():
            self._build_canvas()

        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.drawPixmap(0, 0, self._canvas)

        p.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 80), 1))
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

        cx = int(self._sat * self.width())
        cy = int((1.0 - self._val) * self.height())
        radius = 6
        lum = 0 if self._val > 0.5 else 255
        p.setPen(QtGui.QPen(QtGui.QColor(lum, lum, lum, 200), 1.5))
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawEllipse(QtCore.QPoint(cx, cy), radius, radius)
        p.drawLine(cx - radius - 3, cy, cx + radius + 3, cy)
        p.drawLine(cx, cy - radius - 3, cx, cy + radius + 3)

    def resizeEvent(self, event) -> None:
        self._canvas = None
        super().resizeEvent(event)

    # ── mouse ─────────────────────────────────────────────────────────────────

    def _pick(self, pos: QtCore.QPointF) -> None:
        self._sat = max(0.0, min(1.0, pos.x() / self.width()))
        self._val = max(0.0, min(1.0, 1.0 - pos.y() / self.height()))
        self.update()
        self.colorPicked.emit(self._sat, self._val)

    def mousePressEvent(self, e) -> None:
        self._pick(e.position())

    def mouseMoveEvent(self, e) -> None:
        if e.buttons() & QtCore.Qt.LeftButton:
            self._pick(e.position())

    # ── public API ────────────────────────────────────────────────────────────

    def set_hue(self, hue_deg: float) -> None:
        self._hue_deg = hue_deg
        self._canvas = None
        self.update()

    def set_sat_val(self, sat: float, val: float) -> None:
        self._sat = sat
        self._val = val
        self.update()

    def get_sat(self) -> float:
        return self._sat

    def get_val(self) -> float:
        return self._val