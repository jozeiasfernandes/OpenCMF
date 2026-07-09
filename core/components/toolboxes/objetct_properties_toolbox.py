"""
core.components.toolboxes_manager.object_properties_toolbox
=====================================================
Painel de propriedades de objetos 3-D (transforms + aparência).

Depende de:
  • core.color.ColorPickerWidget  — seletor de cor completo
  • AxisSliderRow                 — slider simples local (específico deste painel)
"""

import sys
from PySide6 import QtWidgets, QtCore, QtGui
from core.color import ColorPickerWidget



# ---------------------------------------------------------------------------
# AxisSliderRow — específico deste painel, não faz parte do color picker
# ---------------------------------------------------------------------------

class AxisSliderRow(QtWidgets.QWidget):
    """Slider horizontal simples com label colorido e spinbox."""
    changed = QtCore.Signal(float)

    def __init__(
        self,
        label: str,
        min_val: float,
        max_val: float,
        default: float,
        decimals: int = 2,
        color: str | None = None,
        parent=None,
    ):
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

        self.slider.valueChanged.connect(self._on_slider)
        self.spin.valueChanged.connect(self._on_spin)

        layout.addWidget(self.lbl)
        layout.addWidget(self.slider)
        layout.addWidget(self.spin)

    def _on_slider(self, val: int) -> None:
        self.spin.blockSignals(True)
        self.spin.setValue(val / self.prec)
        self.spin.blockSignals(False)
        self.changed.emit(self.spin.value())

    def _on_spin(self, val: float) -> None:
        self.slider.blockSignals(True)
        self.slider.setValue(int(val * self.prec))
        self.slider.blockSignals(False)
        self.changed.emit(val)

    def set_value(self, val: float) -> None:
        self.slider.blockSignals(True)
        self.spin.blockSignals(True)
        self.slider.setValue(int(val * self.prec))
        self.spin.setValue(val)
        self.slider.blockSignals(False)
        self.spin.blockSignals(False)

    def get_value(self) -> float:
        return self.spin.value()


# ---------------------------------------------------------------------------
# Vec3SliderWidget
# ---------------------------------------------------------------------------

class Vec3SliderWidget(QtWidgets.QWidget):
    changed = QtCore.Signal(list)

    def __init__(
        self,
        min_val: float,
        max_val: float,
        defaults: tuple = (0.0, 0.0, 0.0),
        decimals: int = 2,
        colors: list | None = None,
        parent=None,
    ):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.rows: list[AxisSliderRow] = []
        colors = colors or ["#ff4b4b", "#4bff4b", "#4b4bff"]
        for lbl, color, d in zip(("X", "Y", "Z"), colors, defaults):
            row = AxisSliderRow(lbl, min_val, max_val, d, decimals=decimals, color=color)
            row.changed.connect(lambda _: self.changed.emit(self.get_values()))
            layout.addWidget(row)
            self.rows.append(row)

    def set_values(self, values: list) -> None:
        for r, v in zip(self.rows, values):
            r.set_value(v)

    def get_values(self) -> list:
        return [r.get_value() for r in self.rows]


# ---------------------------------------------------------------------------
# Component — painel de propriedades
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
        self.current_object_name = None
        self.patient_path = None
        self.object_properties = None
        self._is_initializing = True  # Flag para evitar emissões durante inicialização
        self._setup_ui()
        self._is_initializing = False

    def set_patient_path(self, path: str) -> None:
        """Define o caminho do paciente para salvar alterações."""
        from pathlib import Path
        self.patient_path = Path(path)

    def load_object_properties(self, object_name: str) -> None:
        """Carrega as propriedades de um objeto específico."""
        self.current_object_name = object_name

        if not self.modulo or not hasattr(self.modulo, 'widget_objetos'):
            return

        # Obter propriedades do objeto através do widget de objetos
        props = self.modulo.widget_objetos.get_object_properties(object_name)
        if props:
            self.object_properties = props
            self.load_from_props(props)
        else:
            # Se não encontrou propriedades, limpar painel
            self._clear_properties()

    def _clear_properties(self) -> None:
        """Limpa todas as propriedades do painel."""
        self.vec_pos.set_values([0, 0, 0])
        self.vec_rot.set_values([0, 0, 0])
        self.vec_scl.set_values([1, 1, 1])
        self.color_picker.set_rgb([1, 1, 1])
        self.row_opacity.set_value(1.0)
        self.combo_repr.setCurrentText("Surface")
        self.row_ambient.set_value(0.1)
        self.row_diffuse.set_value(0.7)
        self.row_specular.set_value(0.2)
        self.row_specular_pwr.set_value(10.0)
        self.check_edges.setChecked(False)

    def _save_property_change(self, property_name: str, value) -> None:
        """Salva uma alteração de propriedade no objeto e no arquivo .json."""
        if not self.object_properties or not self.patient_path:
            return

        # Atualizar propriedade no objeto
        if property_name == "position":
            self.object_properties.transform["position"] = value
        elif property_name == "rotation":
            self.object_properties.transform["rotation"] = value
        elif property_name == "scale":
            self.object_properties.transform["scale"] = value
        elif property_name == "color":
            self.object_properties.render["color"] = value
        elif property_name == "opacity":
            self.object_properties.opacity = value
        elif property_name == "representation":
            self.object_properties.render["representation"] = value.lower()
        elif property_name == "ambient":
            self.object_properties.render["ambient"] = value
        elif property_name == "diffuse":
            self.object_properties.render["diffuse"] = value
        elif property_name == "specular":
            self.object_properties.render["specular"] = value
        elif property_name == "specular_power":
            self.object_properties.render["specular_power"] = value
        elif property_name == "edge_visibility":
            self.object_properties.render["edge_visibility"] = value

        # Salvar no arquivo .json
        self._save_to_json()

    def _save_to_json(self) -> None:
        """Salva as propriedades atuais no arquivo .json."""
        if not self.object_properties or not self.patient_path:
            return

        json_path = self.patient_path / self.object_properties.file_path
        try:
            import json
            with open(json_path.with_suffix(".json"), "w", encoding="utf-8") as f:
                json.dump(self.object_properties.to_json(), f, indent=4, ensure_ascii=False)
        except Exception as error:
            print(f"Erro ao salvar propriedades: {error}")

    def _setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # ── Transform ────────────────────────────────────────────────────────
        group_t = QtWidgets.QGroupBox("Transform")
        lay_t = QtWidgets.QFormLayout(group_t)

        self.vec_pos = Vec3SliderWidget(-500.0, 500.0, decimals=2)
        self.vec_rot = Vec3SliderWidget(-180.0, 180.0, decimals=1)
        self.vec_scl = Vec3SliderWidget(0.01, 10.0, defaults=(1, 1, 1), decimals=3)

        self.vec_pos.changed.connect(lambda v: (self._emit_if_not_loading("position", v), self._save_property_change("position", v)))
        self.vec_rot.changed.connect(lambda v: (self._emit_if_not_loading("rotation", v), self._save_property_change("rotation", v)))
        self.vec_scl.changed.connect(lambda v: (self._emit_if_not_loading("scale", v), self._save_property_change("scale", v)))

        lay_t.addRow("Localização:", self.vec_pos)
        lay_t.addRow("Rotação:",     self.vec_rot)
        lay_t.addRow("Escala:",      self.vec_scl)
        layout.addWidget(group_t)

        # ── Aparência ────────────────────────────────────────────────────────
        group_a = QtWidgets.QGroupBox("Aparência")
        lay_a = QtWidgets.QFormLayout(group_a)

        # ColorPickerWidget vem do core.color
        self.color_picker = ColorPickerWidget()
        self.color_picker.colorChanged.connect(lambda c: (self._emit_if_not_loading("color", c), self._save_property_change("color", c)))
        lay_a.addRow("Cor:", self.color_picker)

        self.row_opacity = AxisSliderRow("", 0.0, 1.0, 1.0)
        self.row_opacity.changed.connect(lambda v: (self._emit_if_not_loading("opacity", v), self._save_property_change("opacity", v)))
        lay_a.addRow("Opacidade:", self.row_opacity)

        self.combo_repr = QtWidgets.QComboBox()
        self.combo_repr.addItems(["Surface", "Wireframe", "Points"])
        self.combo_repr.currentTextChanged.connect(lambda t: (self._emit_if_not_loading("representation", t), self._save_property_change("representation", t)))
        lay_a.addRow("Representação:", self.combo_repr)

        self.row_ambient = AxisSliderRow("", 0.0, 1.0, 0.1)
        self.row_ambient.changed.connect(lambda v: (self._emit_if_not_loading("ambient", v), self._save_property_change("ambient", v)))
        lay_a.addRow("Ambiente:", self.row_ambient)

        self.row_diffuse = AxisSliderRow("", 0.0, 1.0, 0.7)
        self.row_diffuse.changed.connect(lambda v: (self._emit_if_not_loading("diffuse", v), self._save_property_change("diffuse", v)))
        lay_a.addRow("Difuso:", self.row_diffuse)

        self.row_specular = AxisSliderRow("", 0.0, 1.0, 0.2)
        self.row_specular.changed.connect(lambda v: (self._emit_if_not_loading("specular", v), self._save_property_change("specular", v)))
        lay_a.addRow("Especular:", self.row_specular)

        self.row_specular_pwr = AxisSliderRow("", 1.0, 128.0, 10.0, decimals=1)
        self.row_specular_pwr.changed.connect(lambda v: (self._emit_if_not_loading("specular_power", v), self._save_property_change("specular_power", v)))
        lay_a.addRow("Brilho:", self.row_specular_pwr)

        self.check_edges = QtWidgets.QCheckBox("Mostrar Arestas")
        self.check_edges.toggled.connect(lambda v: (self._emit_if_not_loading("edge_visibility", v), self._save_property_change("edge_visibility", v)))
        lay_a.addRow("", self.check_edges)

        layout.addWidget(group_a)
        layout.addStretch()

    def load_from_props(self, props) -> None:
        # Flag para evitar emissões durante carregamento
        self._is_loading_props = True
        
        t = props.transform if isinstance(props.transform, dict) else vars(props.transform)
        r = props.render    if isinstance(props.render,    dict) else vars(props.render)

        self.vec_pos.set_values(t.get("position", [0, 0, 0]))
        self.vec_rot.set_values(t.get("rotation", [0, 0, 0]))
        self.vec_scl.set_values(t.get("scale",    [1, 1, 1]))

        self.color_picker.set_rgb(r.get("color", [1, 1, 1]))
        self.row_opacity.set_value(getattr(props, "opacity", 1.0))
        self.combo_repr.setCurrentText(r.get("representation", "surface").capitalize())

        self.row_ambient.set_value(r.get("ambient", 0.1))
        self.row_diffuse.set_value(r.get("diffuse", 0.7))
        self.row_specular.set_value(r.get("specular", 0.2))
        self.row_specular_pwr.set_value(r.get("specular_power", 10.0))
        self.check_edges.setChecked(r.get("edge_visibility", False))
        
        self._is_loading_props = False

    def _emit_if_not_loading(self, property_name: str, value) -> None:
        """Emite o sinal apenas se não estiver carregando propriedades."""
        if not self._is_loading_props:
            if property_name == "position":
                self.positionChanged.emit(value)
            elif property_name == "rotation":
                self.rotationChanged.emit(value)
            elif property_name == "scale":
                self.scaleChanged.emit(value)
            elif property_name == "color":
                self.colorChanged.emit(value)
            elif property_name == "opacity":
                self.opacityChanged.emit(value)
            elif property_name == "representation":
                self.representationChanged.emit(value)
            elif property_name == "ambient":
                self.ambientChanged.emit(value)
            elif property_name == "diffuse":
                self.diffuseChanged.emit(value)
            elif property_name == "specular":
                self.specularChanged.emit(value)
            elif property_name == "specular_power":
                self.specularPowerChanged.emit(value)
            elif property_name == "edge_visibility":
                self.edgeVisibilityChanged.emit(value)


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
            "scale":    [1,  1,  1],
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

    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window,        QtGui.QColor(40,  40,  40))
    pal.setColor(QtGui.QPalette.WindowText,    QtGui.QColor(220, 220, 220))
    pal.setColor(QtGui.QPalette.Base,          QtGui.QColor(30,  30,  30))
    pal.setColor(QtGui.QPalette.Text,          QtGui.QColor(220, 220, 220))
    pal.setColor(QtGui.QPalette.Button,        QtGui.QColor(55,  55,  55))
    pal.setColor(QtGui.QPalette.ButtonText,    QtGui.QColor(220, 220, 220))
    pal.setColor(QtGui.QPalette.Highlight,     QtGui.QColor(80,  120, 200))
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

