"""
core.color.hue_bar
==================
Barra horizontal com o espectro completo de matizes (0–360°).
Emite hueChanged(float) com valor em graus [0, 360).
"""

from PySide6 import QtWidgets, QtCore, QtGui


class HueBar(QtWidgets.QWidget):
    hueChanged = QtCore.Signal(float)   # graus 0.0 – 360.0

    _HEIGHT   = 16
    _CURSOR_W = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self._HEIGHT)
        self.setCursor(QtCore.Qt.CrossCursor)
        self._hue_deg: float = 0.0
        self._bar_pixmap: QtGui.QPixmap | None = None

    # ── rendering ─────────────────────────────────────────────────────────────

    def _build_bar(self) -> None:
        w, h = self.width(), self.height()
        img = QtGui.QImage(w, h, QtGui.QImage.Format_RGB32)
        for x in range(w):
            c = QtGui.QColor.fromHsvF(x / w, 1.0, 1.0)
            for y in range(h):
                img.setPixelColor(x, y, c)
        self._bar_pixmap = QtGui.QPixmap.fromImage(img)

    def paintEvent(self, _event) -> None:
        if self._bar_pixmap is None or self._bar_pixmap.width() != self.width():
            self._build_bar()

        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.drawPixmap(0, 0, self._bar_pixmap)

        p.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 80), 1))
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

        cx = int((self._hue_deg / 360.0) * self.width())
        cw, h = self._CURSOR_W, self.height()
        tri = QtGui.QPolygon([
            QtCore.QPoint(cx,          0),
            QtCore.QPoint(cx - cw // 2, h),
            QtCore.QPoint(cx + cw // 2, h),
        ])
        p.setPen(QtGui.QPen(QtCore.Qt.white, 1.5))
        p.setBrush(QtGui.QColor(30, 30, 30, 180))
        p.drawPolygon(tri)

    def resizeEvent(self, event) -> None:
        self._bar_pixmap = None
        super().resizeEvent(event)

    # ── mouse ─────────────────────────────────────────────────────────────────

    def _pick(self, x: float) -> None:
        self._hue_deg = max(0.0, min(359.99, (x / self.width()) * 360.0))
        self.update()
        self.hueChanged.emit(self._hue_deg)

    def mousePressEvent(self, e) -> None:
        self._pick(e.position().x())

    def mouseMoveEvent(self, e) -> None:
        if e.buttons() & QtCore.Qt.LeftButton:
            self._pick(e.position().x())

    # ── public API ────────────────────────────────────────────────────────────

    def set_hue(self, hue_deg: float) -> None:
        self._hue_deg = max(0.0, min(359.99, hue_deg))
        self.update()

    def get_hue(self) -> float:
        return self._hue_deg