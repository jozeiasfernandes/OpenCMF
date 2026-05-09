"""
core.color.gradient_slider
==========================
Slider cujo groove exibe um gradiente linear live entre duas cores,
mostrando visualmente o efeito de alterar aquele canal.

Emite changed(float) com o valor numérico no intervalo [min_val, max_val].
"""

from PySide6 import QtWidgets, QtCore, QtGui


class GradientSliderRow(QtWidgets.QWidget):
    changed = QtCore.Signal(float)

    _GROOVE_H = 14

    def __init__(
        self,
        label: str,
        min_val: float,
        max_val: float,
        default: float,
        decimals: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._decimals = decimals
        self._left  = QtGui.QColor(0,   0,   0)
        self._right = QtGui.QColor(255, 0,   0)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.lbl = QtWidgets.QLabel(label)
        self.lbl.setFixedWidth(20)
        self.lbl.setStyleSheet(
            "color: #aaa; font-size: 10px; font-weight: bold;")

        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._slider.setRange(0, 1000)
        self._slider.setValue(
            int((default - min_val) / (max_val - min_val) * 1000))
        self._slider.setStyleSheet(self._build_qss())

        self._spin = QtWidgets.QDoubleSpinBox()
        self._spin.setRange(min_val, max_val)
        self._spin.setDecimals(decimals)
        self._spin.setSingleStep(1 if decimals == 0 else 0.01)
        self._spin.setValue(default)
        self._spin.setFixedWidth(52)
        self._spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self._spin.setStyleSheet(
            "QDoubleSpinBox { background:#2a2a2a; color:#eee; "
            "border:1px solid #444; border-radius:3px; padding:1px 3px; }")

        self._slider.valueChanged.connect(self._from_slider)
        self._spin.valueChanged.connect(self._from_spin)

        layout.addWidget(self.lbl)
        layout.addWidget(self._slider, 1)
        layout.addWidget(self._spin)

    # ── QSS ───────────────────────────────────────────────────────────────────

    def _build_qss(self) -> str:
        lc = self._left.name()
        rc = self._right.name()
        h  = self._GROOVE_H
        return (
            f"QSlider::groove:horizontal {{"
            f"  height:{h}px;"
            f"  background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"    stop:0 {lc},stop:1 {rc});"
            f"  border-radius:4px; border:1px solid #333; }}"
            f"QSlider::handle:horizontal {{"
            f"  width:10px; height:{h+6}px; margin:-4px 0;"
            f"  background:white; border:1px solid #666;"
            f"  border-radius:3px; }}"
            f"QSlider::sub-page:horizontal {{ background:transparent; }}"
            f"QSlider::add-page:horizontal  {{ background:transparent; }}"
        )

    # ── sync ──────────────────────────────────────────────────────────────────

    def _from_slider(self, raw: int) -> None:
        val = self._min + (raw / 1000.0) * (self._max - self._min)
        self._spin.blockSignals(True)
        self._spin.setValue(round(val, self._decimals))
        self._spin.blockSignals(False)
        self.changed.emit(self._spin.value())

    def _from_spin(self, val: float) -> None:
        raw = int((val - self._min) / (self._max - self._min) * 1000)
        self._slider.blockSignals(True)
        self._slider.setValue(raw)
        self._slider.blockSignals(False)
        self.changed.emit(val)

    # ── public API ────────────────────────────────────────────────────────────

    def set_gradient(self, left: QtGui.QColor, right: QtGui.QColor) -> None:
        self._left  = left
        self._right = right
        self._slider.setStyleSheet(self._build_qss())

    def set_value(self, val: float) -> None:
        self._slider.blockSignals(True)
        self._spin.blockSignals(True)
        raw = int((val - self._min) / (self._max - self._min) * 1000)
        self._slider.setValue(raw)
        self._spin.setValue(round(val, self._decimals))
        self._slider.blockSignals(False)
        self._spin.blockSignals(False)

    def get_value(self) -> float:
        return self._spin.value()