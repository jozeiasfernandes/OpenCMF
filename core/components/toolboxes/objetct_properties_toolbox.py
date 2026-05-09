import sys
from PySide6 import QtWidgets, QtCore, QtGui


# ---------------------------------------------------------------------------
# AxisSliderRow — unchanged from original
# ---------------------------------------------------------------------------

class AxisSliderRow(QtWidgets.QWidget):
    changed = QtCore.Signal(float)

    def __init__(self, label: str, min_val: float, max_val: float, default: float,
                 decimals: int = 2, color=None, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.lbl = QtWidgets.QLabel(label)
        self.lbl.setFixedWidth(14)
        if color:
            self.lbl.setStyleSheet(f"color: {color}; font-weight: bold;")

        self.prec = 10 ** decimals
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(int(min_val * self.prec), int(max_val * self.prec))
        self.slider.setValue(int(default * self.prec))

        self.spin = QtWidgets.QDoubleSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setDecimals(decimals)
        self.spin.setSingleStep(0.1)
        self.spin.setValue(default)
        self.spin.setFixedWidth(65)
        self.spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spin.valueChanged.connect(self._on_spin_changed)

        layout.addWidget(self.lbl)
        layout.addWidget(self.slider)
        layout.addWidget(self.spin)

    def _on_slider_changed(self, val: int):
        self.spin.blockSignals(True)
        self.spin.setValue(val / self.prec)
        self.spin.blockSignals(False)
        self.changed.emit(self.spin.value())

    def _on_spin_changed(self, val: float):
        self.slider.blockSignals(True)
        self.slider.setValue(int(val * self.prec))
        self.slider.blockSignals(False)
        self.changed.emit(val)

    def set_value(self, val: float):
        self.slider.blockSignals(True)
        self.spin.blockSignals(True)
        self.slider.setValue(int(val * self.prec))
        self.spin.setValue(val)
        self.slider.blockSignals(False)
        self.spin.blockSignals(False)

    def get_value(self) -> float:
        return self.spin.value()


# ---------------------------------------------------------------------------
# HueBar — horizontal bar showing full hue spectrum (0–360°)
# ---------------------------------------------------------------------------

class HueBar(QtWidgets.QWidget):
    hueChanged = QtCore.Signal(float)   # 0.0 – 1.0

    _H = 16   # bar height in pixels
    _CW = 10  # cursor width

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self._H)
        self.setCursor(QtCore.Qt.CrossCursor)
        self._hue = 0.0          # 0.0 – 1.0
        self._bar_pixmap = None

    # ------------------------------------------------------------------ paint

    def resizeEvent(self, event):
        self._bar_pixmap = None   # rebuild on next paint
        super().resizeEvent(event)

    def _build_bar(self):
        w, h = self.width(), self.height()
        img = QtGui.QImage(w, h, QtGui.QImage.Format_RGB32)
        for x in range(w):
            hue = x / w
            c = QtGui.QColor.fromHsvF(hue, 1.0, 1.0)
            for y in range(h):
                img.setPixelColor(x, y, c)
        self._bar_pixmap = QtGui.QPixmap.fromImage(img)

    def paintEvent(self, event):
        if self._bar_pixmap is None or self._bar_pixmap.width() != self.width():
            self._build_bar()

        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        # draw bar
        p.drawPixmap(0, 0, self._bar_pixmap)

        # border
        p.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 80), 1))
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # cursor triangle
        cx = int(self._hue * self.width())
        cw, h = self._CW, self.height()
        tri = QtGui.QPolygon([
            QtCore.QPoint(cx,          0),
            QtCore.QPoint(cx - cw // 2, h),
            QtCore.QPoint(cx + cw // 2, h),
        ])
        p.setPen(QtGui.QPen(QtCore.Qt.white, 1.5))
        p.setBrush(QtGui.QColor(30, 30, 30, 180))
        p.drawPolygon(tri)

    # ------------------------------------------------------------------ mouse

    def _set_from_x(self, x):
        self._hue = max(0.0, min(1.0, x / self.width()))
        self.update()
        self.hueChanged.emit(self._hue)

    def mousePressEvent(self, e):
        self._set_from_x(e.position().x())

    def mouseMoveEvent(self, e):
        if e.buttons() & QtCore.Qt.LeftButton:
            self._set_from_x(e.position().x())

    # ------------------------------------------------------------------ API

    def set_hue(self, h: float):
        self._hue = max(0.0, min(1.0, h))
        self.update()

    def get_hue(self) -> float:
        return self._hue


# ---------------------------------------------------------------------------
# SatValCanvas — 2-D gradient square: X = saturation, Y = value
# ---------------------------------------------------------------------------

class SatValCanvas(QtWidgets.QWidget):
    colorPicked = QtCore.Signal(float, float)   # sat, val  0.0 – 1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 140)
        self.setCursor(QtCore.Qt.CrossCursor)
        self._hue = 0.0
        self._sat = 1.0
        self._val = 1.0
        self._canvas = None

    # ------------------------------------------------------------------ paint

    def _build_canvas(self):
        w, h = self.width(), self.height()
        img = QtGui.QImage(w, h, QtGui.QImage.Format_RGB32)
        base = QtGui.QColor.fromHsvF(self._hue, 1.0, 1.0)
        for x in range(w):
            sat = x / w
            for y in range(h):
                val = 1.0 - (y / h)
                # blend: white → hue → black
                r = int((1 - sat) * 255 + sat * val * base.red())
                g = int((1 - sat) * 255 + sat * val * base.green())
                b = int((1 - sat) * 255 + sat * val * base.blue())
                img.setPixelColor(x, y, QtGui.QColor(r, g, b))
        self._canvas = QtGui.QPixmap.fromImage(img)

    def paintEvent(self, event):
        if self._canvas is None or self._canvas.width() != self.width():
            self._build_canvas()

        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.drawPixmap(0, 0, self._canvas)

        # border
        p.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 80), 1))
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # crosshair cursor
        cx = int(self._sat * self.width())
        cy = int((1.0 - self._val) * self.height())
        r = 6
        lum = 0 if self._val > 0.5 else 255
        p.setPen(QtGui.QPen(QtGui.QColor(lum, lum, lum, 200), 1.5))
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawEllipse(QtCore.QPoint(cx, cy), r, r)
        p.drawLine(cx - r - 3, cy, cx + r + 3, cy)
        p.drawLine(cx, cy - r - 3, cx, cy + r + 3)

    def resizeEvent(self, event):
        self._canvas = None
        super().resizeEvent(event)

    # ------------------------------------------------------------------ mouse

    def _pick(self, pos):
        self._sat = max(0.0, min(1.0, pos.x() / self.width()))
        self._val = max(0.0, min(1.0, 1.0 - pos.y() / self.height()))
        self.update()
        self.colorPicked.emit(self._sat, self._val)

    def mousePressEvent(self, e):
        self._pick(e.position())

    def mouseMoveEvent(self, e):
        if e.buttons() & QtCore.Qt.LeftButton:
            self._pick(e.position())

    # ------------------------------------------------------------------ API

    def set_hue(self, h: float):
        self._hue = h
        self._canvas = None
        self.update()

    def set_sat_val(self, s: float, v: float):
        self._sat = s
        self._val = v
        self.update()

    def get_sat(self) -> float:
        return self._sat

    def get_val(self) -> float:
        return self._val


# ---------------------------------------------------------------------------
# GradientSliderRow — label + gradient-painted slider + spinbox
# ---------------------------------------------------------------------------

class GradientSliderRow(QtWidgets.QWidget):
    """Slider whose groove is painted with a live color gradient."""
    changed = QtCore.Signal(float)

    _H = 14   # groove height

    def __init__(self, label: str, min_val: float, max_val: float, default: float,
                 decimals: int = 0, parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._decimals = decimals
        self._left_color  = QtGui.QColor(0,   0,   0)
        self._right_color = QtGui.QColor(255, 0,   0)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.lbl = QtWidgets.QLabel(label)
        self.lbl.setFixedWidth(20)
        self.lbl.setStyleSheet("color: #aaa; font-size: 10px; font-weight: bold;")

        # Custom groove + handle on a QSlider
        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._slider.setRange(0, 1000)
        self._slider.setValue(int((default - min_val) / (max_val - min_val) * 1000))
        self._slider.setStyleSheet(self._build_qss())

        prec = 10 ** decimals
        self._spin = QtWidgets.QDoubleSpinBox()
        self._spin.setRange(min_val, max_val)
        self._spin.setDecimals(decimals)
        self._spin.setSingleStep(1 if decimals == 0 else 0.01)
        self._spin.setValue(default)
        self._spin.setFixedWidth(52)
        self._spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self._spin.setStyleSheet("QDoubleSpinBox { background: #2a2a2a; color: #eee; "
                                 "border: 1px solid #444; border-radius: 3px; padding: 1px 3px; }")

        self._slider.valueChanged.connect(self._from_slider)
        self._spin.valueChanged.connect(self._from_spin)

        layout.addWidget(self.lbl)
        layout.addWidget(self._slider, 1)
        layout.addWidget(self._spin)

    # ------------------------------------------------------------------ style

    def _build_qss(self):
        # We paint the gradient via a stylesheet linear-gradient using the
        # current left/right colors. Rebuilt whenever colors change.
        lc = self._left_color.name()
        rc = self._right_color.name()
        return f"""
            QSlider::groove:horizontal {{
                height: {self._H}px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {lc}, stop:1 {rc});
                border-radius: 4px;
                border: 1px solid #333;
            }}
            QSlider::handle:horizontal {{
                width: 10px;
                height: {self._H + 6}px;
                margin: -4px 0;
                background: white;
                border: 1px solid #666;
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{ background: transparent; }}
            QSlider::add-page:horizontal {{ background: transparent; }}
        """

    def set_gradient(self, left: QtGui.QColor, right: QtGui.QColor):
        self._left_color  = left
        self._right_color = right
        self._slider.setStyleSheet(self._build_qss())

    # ------------------------------------------------------------------ sync

    def _from_slider(self, raw: int):
        val = self._min + (raw / 1000.0) * (self._max - self._min)
        self._spin.blockSignals(True)
        self._spin.setValue(round(val, self._decimals))
        self._spin.blockSignals(False)
        self.changed.emit(self._spin.value())

    def _from_spin(self, val: float):
        raw = int((val - self._min) / (self._max - self._min) * 1000)
        self._slider.blockSignals(True)
        self._slider.setValue(raw)
        self._slider.blockSignals(False)
        self.changed.emit(val)

    # ------------------------------------------------------------------ API

    def set_value(self, val: float):
        self._slider.blockSignals(True)
        self._spin.blockSignals(True)
        raw = int((val - self._min) / (self._max - self._min) * 1000)
        self._slider.setValue(raw)
        self._spin.setValue(round(val, self._decimals))
        self._slider.blockSignals(False)
        self._spin.blockSignals(False)

    def get_value(self) -> float:
        return self._spin.value()


# ---------------------------------------------------------------------------
# ColorPickerWidget  (full rewrite)
# ---------------------------------------------------------------------------

class ColorPickerWidget(QtWidgets.QWidget):
    """
    Colour picker with:
      • 2-D Saturation/Value canvas
      • Hue bar
      • Mode switch: RGB | HSV | CMYK
      • Gradient sliders (each shows what changing that channel does)
      • Hex input
      • Eyedropper (native QColorDialog)
    """
    colorChanged = QtCore.Signal(list)   # [r, g, b]  floats 0–1

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rgb = [1.0, 1.0, 1.0]   # master state (floats 0–1)
        self._updating = False
        self._setup_ui()
        self._rebuild_sliders()

    # ================================================================= UI

    def _setup_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(5)

        # ---- 2-D canvas
        self._canvas = SatValCanvas()
        self._canvas.colorPicked.connect(self._canvas_picked)
        root.addWidget(self._canvas)

        # ---- Hue bar
        self._hue_bar = HueBar()
        self._hue_bar.hueChanged.connect(self._hue_changed)
        root.addWidget(self._hue_bar)

        # ---- top row: mode combo + hex + eyedropper
        top = QtWidgets.QHBoxLayout()
        top.setSpacing(4)

        self._combo_mode = QtWidgets.QComboBox()
        self._combo_mode.addItems(["RGB", "HSV", "CMYK"])
        self._combo_mode.setFixedWidth(62)
        self._combo_mode.setStyleSheet(
            "QComboBox { background:#2a2a2a; color:#eee; border:1px solid #444; "
            "border-radius:3px; padding:1px 4px; }"
            "QComboBox::drop-down { border:none; }"
            "QComboBox QAbstractItemView { background:#222; color:#eee; }"
        )
        self._combo_mode.currentIndexChanged.connect(self._mode_changed)

        self._preview = QtWidgets.QLabel()
        self._preview.setFixedSize(28, 22)
        self._preview.setStyleSheet("border:1px solid #555; border-radius:3px;")

        self._hex_edit = QtWidgets.QLineEdit()
        self._hex_edit.setFixedWidth(72)
        self._hex_edit.setPlaceholderText("#RRGGBB")
        self._hex_edit.setStyleSheet(
            "QLineEdit { background:#2a2a2a; color:#eee; border:1px solid #444; "
            "border-radius:3px; padding:1px 4px; font-family:monospace; }"
        )
        self._hex_edit.editingFinished.connect(self._hex_entered)

        self._btn_eye = QtWidgets.QPushButton("⊕")
        self._btn_eye.setFixedSize(26, 22)
        self._btn_eye.setToolTip("Abrir seletor de cores do sistema")
        self._btn_eye.setStyleSheet(
            "QPushButton { background:#2a2a2a; color:#eee; border:1px solid #444; "
            "border-radius:3px; font-size:14px; }"
            "QPushButton:hover { background:#3a3a3a; }"
        )
        self._btn_eye.clicked.connect(self._open_dialog)

        top.addWidget(self._combo_mode)
        top.addWidget(self._preview)
        top.addWidget(self._hex_edit)
        top.addStretch()
        top.addWidget(self._btn_eye)
        root.addLayout(top)

        # ---- gradient slider area (rebuilt per mode)
        self._slider_container = QtWidgets.QWidget()
        self._slider_layout = QtWidgets.QVBoxLayout(self._slider_container)
        self._slider_layout.setContentsMargins(0, 0, 0, 0)
        self._slider_layout.setSpacing(3)
        root.addWidget(self._slider_container)

        self._sliders: list[GradientSliderRow] = []

    # ================================================================= slider construction

    def _clear_sliders(self):
        for s in self._sliders:
            s.changed.disconnect()
        self._sliders.clear()
        while self._slider_layout.count():
            item = self._slider_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_slider(self, label, lo, hi, default, decimals=0) -> GradientSliderRow:
        row = GradientSliderRow(label, lo, hi, default, decimals=decimals)
        self._slider_layout.addWidget(row)
        self._sliders.append(row)
        return row

    def _rebuild_sliders(self):
        self._clear_sliders()
        mode = self._combo_mode.currentText() if hasattr(self, '_combo_mode') else "RGB"

        if mode == "RGB":
            self._add_slider("R", 0, 255, 255, 0)
            self._add_slider("G", 0, 255, 255, 0)
            self._add_slider("B", 0, 255, 255, 0)
        elif mode == "HSV":
            self._add_slider("H", 0, 360, 0,   0)
            self._add_slider("S", 0, 100, 100, 0)
            self._add_slider("V", 0, 100, 100, 0)
        else:  # CMYK
            self._add_slider("C", 0, 100, 0, 0)
            self._add_slider("M", 0, 100, 0, 0)
            self._add_slider("Y", 0, 100, 0, 0)
            self._add_slider("K", 0, 100, 0, 0)

        for s in self._sliders:
            s.changed.connect(self._sliders_changed)

        self._update_all_from_rgb()

    # ================================================================= conversions

    @staticmethod
    def _rgb_to_hsv(r, g, b):
        c = QtGui.QColor.fromRgbF(r, g, b)
        return c.hueF(), c.saturationF(), c.valueF()

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        c = QtGui.QColor.fromHsvF(max(0.0, h), s, v)
        return c.redF(), c.greenF(), c.blueF()

    @staticmethod
    def _rgb_to_cmyk(r, g, b):
        k = 1.0 - max(r, g, b)
        if k == 1.0:
            return 0.0, 0.0, 0.0, 1.0
        c = (1.0 - r - k) / (1.0 - k)
        m = (1.0 - g - k) / (1.0 - k)
        y = (1.0 - b - k) / (1.0 - k)
        return c, m, y, k

    @staticmethod
    def _cmyk_to_rgb(c, m, y, k):
        r = (1 - c) * (1 - k)
        g = (1 - m) * (1 - k)
        b = (1 - y) * (1 - k)
        return r, g, b

    # ================================================================= gradient colors for each slider

    def _update_slider_gradients(self):
        r, g, b = self._rgb
        mode = self._combo_mode.currentText()

        if mode == "RGB":
            R, G, B = int(r*255), int(g*255), int(b*255)
            self._sliders[0].set_gradient(QtGui.QColor(0, G, B),   QtGui.QColor(255, G, B))
            self._sliders[1].set_gradient(QtGui.QColor(R, 0, B),   QtGui.QColor(R, 255, B))
            self._sliders[2].set_gradient(QtGui.QColor(R, G, 0),   QtGui.QColor(R, G, 255))

        elif mode == "HSV":
            h, s, v = self._rgb_to_hsv(r, g, b)

            # H: sweep all hues at current S and V
            hue_colors = []
            steps = 6
            for i in range(steps + 1):
                hf = i / steps
                cr, cg, cb = self._hsv_to_rgb(hf, s, v)
                hue_colors.append(QtGui.QColor.fromRgbF(cr, cg, cb))

            # build multi-stop gradient via QLinearGradient rendered to pixmap — but
            # GradientSliderRow only takes two stops.  Use the "zero-hue" and "full-hue"
            # approximation: left = grey (s=0), right = pure hue (s=1, v=1).
            # For hue slider: left = current colour at h=0, right = h=1 (same as h=0)
            # Better: show hue=0 → hue=1 at current sv  (approximation with 2 stops)
            cl = QtGui.QColor.fromRgbF(*self._hsv_to_rgb(0.0, s, v))
            cr2= QtGui.QColor.fromRgbF(*self._hsv_to_rgb(1.0, s, v))
            self._sliders[0].set_gradient(cl, cr2)

            # S: grey → full hue
            self._sliders[1].set_gradient(
                QtGui.QColor.fromRgbF(*self._hsv_to_rgb(h, 0.0, v)),
                QtGui.QColor.fromRgbF(*self._hsv_to_rgb(h, 1.0, v)),
            )
            # V: black → full hue at s
            self._sliders[2].set_gradient(
                QtGui.QColor(0, 0, 0),
                QtGui.QColor.fromRgbF(*self._hsv_to_rgb(h, s, 1.0)),
            )

        else:  # CMYK
            c0, m0, y0, k0 = self._rgb_to_cmyk(r, g, b)
            # C: no cyan → full cyan
            self._sliders[0].set_gradient(
                QtGui.QColor.fromRgbF(*self._cmyk_to_rgb(0, m0, y0, k0)),
                QtGui.QColor.fromRgbF(*self._cmyk_to_rgb(1, m0, y0, k0)),
            )
            # M
            self._sliders[1].set_gradient(
                QtGui.QColor.fromRgbF(*self._cmyk_to_rgb(c0, 0, y0, k0)),
                QtGui.QColor.fromRgbF(*self._cmyk_to_rgb(c0, 1, y0, k0)),
            )
            # Y
            self._sliders[2].set_gradient(
                QtGui.QColor.fromRgbF(*self._cmyk_to_rgb(c0, m0, 0, k0)),
                QtGui.QColor.fromRgbF(*self._cmyk_to_rgb(c0, m0, 1, k0)),
            )
            # K: white (k=0) → black (k=1)
            self._sliders[3].set_gradient(
                QtGui.QColor.fromRgbF(*self._cmyk_to_rgb(c0, m0, y0, 0)),
                QtGui.QColor.fromRgbF(*self._cmyk_to_rgb(c0, m0, y0, 1)),
            )

    # ================================================================= update helpers

    def _update_all_from_rgb(self):
        """Push current _rgb into canvas, hue bar, sliders, hex, preview."""
        if self._updating:
            return
        self._updating = True
        try:
            r, g, b = self._rgb
            h, s, v = self._rgb_to_hsv(r, g, b)

            # canvas + hue bar
            self._canvas.set_hue(max(0.0, h))
            self._canvas.set_sat_val(s, v)
            self._hue_bar.set_hue(max(0.0, h))

            # sliders
            mode = self._combo_mode.currentText()
            if mode == "RGB":
                vals = [r * 255, g * 255, b * 255]
            elif mode == "HSV":
                vals = [max(0.0, h) * 360, s * 100, v * 100]
            else:
                c, m, y, k = self._rgb_to_cmyk(r, g, b)
                vals = [c * 100, m * 100, y * 100, k * 100]

            for sl, val in zip(self._sliders, vals):
                sl.set_value(val)

            self._update_slider_gradients()
            self._update_preview()
        finally:
            self._updating = False

    def _update_preview(self):
        qc = QtGui.QColor.fromRgbF(*self._rgb)
        self._preview.setStyleSheet(
            f"background:{qc.name()}; border:1px solid #555; border-radius:3px;")
        # hex
        self._hex_edit.blockSignals(True)
        self._hex_edit.setText(qc.name().upper())
        self._hex_edit.blockSignals(False)

    # ================================================================= event handlers

    def _canvas_picked(self, sat: float, val: float):
        h = self._hue_bar.get_hue()
        r, g, b = self._hsv_to_rgb(h, sat, val)
        self._rgb = [r, g, b]
        self._update_all_from_rgb()
        self.colorChanged.emit(self._rgb)

    def _hue_changed(self, h: float):
        # keep current sat/val, only hue changes
        _, s, v = self._rgb_to_hsv(*self._rgb)
        self._canvas.set_hue(h)
        r, g, b = self._hsv_to_rgb(h, s, v)
        self._rgb = [r, g, b]
        self._update_all_from_rgb()
        self.colorChanged.emit(self._rgb)

    def _sliders_changed(self, _val: float):
        if self._updating:
            return
        mode = self._combo_mode.currentText()
        vals = [s.get_value() for s in self._sliders]

        if mode == "RGB":
            self._rgb = [vals[0]/255, vals[1]/255, vals[2]/255]
        elif mode == "HSV":
            self._rgb = list(self._hsv_to_rgb(vals[0]/360, vals[1]/100, vals[2]/100))
        else:
            self._rgb = list(self._cmyk_to_rgb(
                vals[0]/100, vals[1]/100, vals[2]/100, vals[3]/100))

        self._update_all_from_rgb()
        self.colorChanged.emit(self._rgb)

    def _mode_changed(self):
        self._rebuild_sliders()

    def _hex_entered(self):
        txt = self._hex_edit.text().strip()
        if not txt.startswith("#"):
            txt = "#" + txt
        qc = QtGui.QColor(txt)
        if qc.isValid():
            self._rgb = [qc.redF(), qc.greenF(), qc.blueF()]
            self._update_all_from_rgb()
            self.colorChanged.emit(self._rgb)

    def _open_dialog(self):
        qc = QtGui.QColor.fromRgbF(*self._rgb)
        chosen = QtWidgets.QColorDialog.getColor(qc, self)
        if chosen.isValid():
            self._rgb = [chosen.redF(), chosen.greenF(), chosen.blueF()]
            self._update_all_from_rgb()
            self.colorChanged.emit(self._rgb)

    # ================================================================= public API

    def set_rgb(self, rgb: list):
        self._rgb = [float(v) for v in rgb]
        self._update_all_from_rgb()

    def get_rgb(self) -> list:
        return list(self._rgb)


# ---------------------------------------------------------------------------
# Vec3SliderWidget — unchanged from original
# ---------------------------------------------------------------------------

class Vec3SliderWidget(QtWidgets.QWidget):
    changed = QtCore.Signal(list)

    def __init__(self, min_val, max_val, defaults=(0.0, 0.0, 0.0), decimals=2, colors=None, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.rows = []
        labels = ("X", "Y", "Z")
        colors = colors or ["#ff4b4b", "#4bff4b", "#4b4bff"]
        for lbl, color, d in zip(labels, colors, defaults):
            row = AxisSliderRow(lbl, min_val, max_val, d, decimals=decimals, color=color)
            row.changed.connect(lambda _: self.changed.emit(self.get_values()))
            layout.addWidget(row)
            self.rows.append(row)

    def set_values(self, values):
        for r, v in zip(self.rows, values):
            r.set_value(v)

    def get_values(self):
        return [r.get_value() for r in self.rows]


# ---------------------------------------------------------------------------
# Component — Properties panel  (same public API, updated color_picker)
# ---------------------------------------------------------------------------

class Component(QtWidgets.QWidget):
    toolbox_name = "Propriedades"

    positionChanged       = QtCore.Signal(list)
    rotationChanged       = QtCore.Signal(list)
    scaleChanged          = QtCore.Signal(list)
    colorChanged          = QtCore.Signal(list)
    opacityChanged        = QtCore.Signal(float)
    representationChanged = QtCore.Signal(str)
    ambientChanged        = QtCore.Signal(float)
    diffuseChanged        = QtCore.Signal(float)
    specularChanged       = QtCore.Signal(float)
    specularPowerChanged  = QtCore.Signal(float)
    edgeVisibilityChanged = QtCore.Signal(bool)

    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # GRUPO TRANSFORM
        group_t = QtWidgets.QGroupBox("Transform")
        lay_t = QtWidgets.QFormLayout(group_t)
        self.vec_pos = Vec3SliderWidget(-500.0, 500.0, decimals=2)
        self.vec_rot = Vec3SliderWidget(-180.0, 180.0, decimals=1)
        self.vec_scl = Vec3SliderWidget(0.01, 10.0, defaults=(1, 1, 1), decimals=3)

        self.vec_pos.changed.connect(self.positionChanged.emit)
        self.vec_rot.changed.connect(self.rotationChanged.emit)
        self.vec_scl.changed.connect(self.scaleChanged.emit)

        lay_t.addRow("Localização:", self.vec_pos)
        lay_t.addRow("Rotação:",     self.vec_rot)
        lay_t.addRow("Escala:",      self.vec_scl)
        layout.addWidget(group_t)

        # GRUPO APARÊNCIA
        group_a = QtWidgets.QGroupBox("Aparência")
        lay_a = QtWidgets.QFormLayout(group_a)

        self.color_picker = ColorPickerWidget()
        self.color_picker.colorChanged.connect(self.colorChanged.emit)
        lay_a.addRow("Cor:", self.color_picker)

        self.row_opacity = AxisSliderRow("", 0.0, 1.0, 1.0)
        self.row_opacity.changed.connect(self.opacityChanged.emit)
        lay_a.addRow("Opacidade:", self.row_opacity)

        self.combo_repr = QtWidgets.QComboBox()
        self.combo_repr.addItems(["Surface", "Wireframe", "Points"])
        self.combo_repr.currentTextChanged.connect(self.representationChanged.emit)
        lay_a.addRow("Representação:", self.combo_repr)

        self.row_ambient = AxisSliderRow("", 0.0, 1.0, 0.1)
        self.row_ambient.changed.connect(self.ambientChanged.emit)
        lay_a.addRow("Ambiente:", self.row_ambient)

        self.row_diffuse = AxisSliderRow("", 0.0, 1.0, 0.7)
        self.row_diffuse.changed.connect(self.diffuseChanged.emit)
        lay_a.addRow("Difuso:", self.row_diffuse)

        self.row_specular = AxisSliderRow("", 0.0, 1.0, 0.2)
        self.row_specular.changed.connect(self.specularChanged.emit)
        lay_a.addRow("Especular:", self.row_specular)

        self.row_specular_pwr = AxisSliderRow("", 1.0, 128.0, 10.0, decimals=1)
        self.row_specular_pwr.changed.connect(self.specularPowerChanged.emit)
        lay_a.addRow("Brilho:", self.row_specular_pwr)

        self.check_edges = QtWidgets.QCheckBox("Mostrar Arestas")
        self.check_edges.toggled.connect(self.edgeVisibilityChanged.emit)
        lay_a.addRow("", self.check_edges)

        layout.addWidget(group_a)
        layout.addStretch()

    def load_from_props(self, props):
        t = props.transform if isinstance(props.transform, dict) else vars(props.transform)
        r = props.render    if isinstance(props.render,    dict) else vars(props.render)

        self.vec_pos.set_values(t.get("position", [0, 0, 0]))
        self.vec_rot.set_values(t.get("rotation", [0, 0, 0]))
        self.vec_scl.set_values(t.get("scale",    [1, 1, 1]))

        self.color_picker.set_rgb(r.get("color", [1, 1, 1]))
        self.row_opacity.set_value(getattr(props, 'opacity', 1.0))
        self.combo_repr.setCurrentText(r.get("representation", "surface").capitalize())

        self.row_ambient.set_value(r.get("ambient", 0.1))
        self.row_diffuse.set_value(r.get("diffuse", 0.7))
        self.row_specular.set_value(r.get("specular", 0.2))
        self.row_specular_pwr.set_value(r.get("specular_power", 10.0))
        self.check_edges.setChecked(r.get("edge_visibility", False))


# ---------------------------------------------------------------------------
# __main__
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from dataclasses import dataclass, field

    @dataclass
    class FakeProps:
        id: str = "123"
        opacity: float = 0.8
        transform: dict = field(default_factory=lambda: {
            "position": [10, 20, 30],
            "rotation": [0, 45, 0],
            "scale":    [1, 1, 1],
        })
        render: dict = field(default_factory=lambda: {
            "color":           [0.2, 0.6, 1.0],
            "representation":  "surface",
            "ambient":         0.2,
            "diffuse":         0.8,
            "specular":        0.5,
            "specular_power":  25.0,
            "edge_visibility": True,
        })

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # dark palette
    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window,          QtGui.QColor(40,  40,  40))
    pal.setColor(QtGui.QPalette.WindowText,      QtGui.QColor(220, 220, 220))
    pal.setColor(QtGui.QPalette.Base,            QtGui.QColor(30,  30,  30))
    pal.setColor(QtGui.QPalette.AlternateBase,   QtGui.QColor(45,  45,  45))
    pal.setColor(QtGui.QPalette.Text,            QtGui.QColor(220, 220, 220))
    pal.setColor(QtGui.QPalette.Button,          QtGui.QColor(55,  55,  55))
    pal.setColor(QtGui.QPalette.ButtonText,      QtGui.QColor(220, 220, 220))
    pal.setColor(QtGui.QPalette.Highlight,       QtGui.QColor(80,  120, 200))
    pal.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    app.setPalette(pal)

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("OpenCMF — Properties Editor")
    win.resize(400, 860)

    comp = Component()
    comp.load_from_props(FakeProps())

    scroll = QtWidgets.QScrollArea()
    scroll.setWidget(comp)
    scroll.setWidgetResizable(True)
    win.setCentralWidget(scroll)
    win.show()
    sys.exit(app.exec())