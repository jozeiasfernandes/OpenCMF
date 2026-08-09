from typing import Optional, Any
import sys
import json
import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from application.colors import ColorPickerWidget
from core.components.bases.base_sidepanel import BaseSidePanel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ObjectProperties_SidePanel (Painel Principal)
# ---------------------------------------------------------------------------

class ObjectProperties_SidePanel(BaseSidePanel):
    side_panel_name = "Propriedades do Objeto"

    def __init__(self, context: Any, title: str = "", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, title=title, parent=parent)

        self.current_object_id = None
        self.current_object_name = ""
        self._is_loading_props = False

    def setup_ui(self) -> None:
        """Configura a interface usando o layout herdado de BaseSidePanel."""
        self.layout.setSpacing(8)

        # ── Transform ────────────────────────────────────────────────────────
        group_t = QtWidgets.QGroupBox("Transform")
        lay_t = QtWidgets.QFormLayout(group_t)

        self.vec_pos = Vec3SliderWidget(-500.0, 500.0, decimals=2)
        self.vec_rot = Vec3SliderWidget(-180.0, 180.0, decimals=1)
        self.vec_scl = Vec3SliderWidget(0.01, 10.0, defaults=(1, 1, 1), decimals=3)

        self.vec_pos.changed.connect(lambda v: self._dispatch("position", v))
        self.vec_rot.changed.connect(lambda v: self._dispatch("rotation", v))
        self.vec_scl.changed.connect(lambda v: self._dispatch("scale", v))

        lay_t.addRow("Localização:", self.vec_pos)
        lay_t.addRow("Rotação:", self.vec_rot)
        lay_t.addRow("Escala:", self.vec_scl)
        self.layout.addWidget(group_t)

        # ── Aparência ────────────────────────────────────────────────────────
        group_a = QtWidgets.QGroupBox("Aparência")
        lay_a = QtWidgets.QFormLayout(group_a)

        self.color_picker = ColorPickerWidget()
        self.color_picker.colorChanged.connect(lambda c: self._dispatch("colors", c))
        lay_a.addRow("Cor:", self.color_picker)

        self.row_opacity = AxisSliderRow("Opacidade", 0.0, 1.0, 1.0)
        self.row_opacity.changed.connect(lambda v: self._dispatch("opacity", v))
        lay_a.addRow(self.row_opacity)

        self.combo_repr = QtWidgets.QComboBox()
        self.combo_repr.addItems(["Surface", "Wireframe", "Points"])
        self.combo_repr.currentTextChanged.connect(lambda t: self._dispatch("representation", t))
        lay_a.addRow("Representação:", self.combo_repr)

        self.row_ambient = AxisSliderRow("Ambiente", 0.0, 1.0, 0.1)
        self.row_ambient.changed.connect(lambda v: self._dispatch("ambient", v))
        lay_a.addRow(self.row_ambient)

        self.row_diffuse = AxisSliderRow("Difuso", 0.0, 1.0, 0.7)
        self.row_diffuse.changed.connect(lambda v: self._dispatch("diffuse", v))
        lay_a.addRow(self.row_diffuse)

        self.row_specular = AxisSliderRow("Especular", 0.0, 1.0, 0.2)
        self.row_specular.changed.connect(lambda v: self._dispatch("specular", v))
        lay_a.addRow(self.row_specular)

        self.row_specular_pwr = AxisSliderRow("Brilho", 1.0, 128.0, 10.0, decimals=1)
        self.row_specular_pwr.changed.connect(lambda v: self._dispatch("specular_power", v))
        lay_a.addRow(self.row_specular_pwr)

        self.check_edges = QtWidgets.QCheckBox("Mostrar Arestas")
        self.check_edges.toggled.connect(lambda v: self._dispatch("edge_visibility", v))
        lay_a.addRow(self.check_edges)

        self.layout.addWidget(group_a)
        self.layout.addStretch()

    def _dispatch(self, property_name: str, value: Any) -> None:
        if self._is_loading_props or not self.current_object_id:
            return

        try:
            self._save_property_change(property_name, value)
            if self.event_bus:
                event_name = f"object_{property_name}_changed"
                payload = {
                    "object_id": self.current_object_id,
                    "object_name": self.current_object_name,
                    "value": value
                }
                self.event_bus.emit(event_name, payload)

        except Exception as e:
            logger.error(f"Erro ao disparar evento {property_name} para o objeto {self.current_object_id}: {e}")

    def load_from_props(self, props) -> None:
        """Carrega propriedades tratando dados de dicts ou objetos (dataclasses)."""
        self._is_loading_props = True

        t = props.transform if isinstance(props.transform, dict) else vars(props.transform)
        r = props.render if isinstance(props.render, dict) else vars(props.render)

        try:
            self.vec_pos.set_values(t.get("position", [0, 0, 0]))
            self.vec_rot.set_values(t.get("rotation", [0, 0, 0]))
            self.vec_scl.set_values(t.get("scale", [1, 1, 1]))

            self.color_picker.set_rgb(r.get("colors", [1.0, 1.0, 1.0]))
            self.row_opacity.set_value(getattr(props, "opacity", 1.0))

            repr_val = r.get("representation", "surface")
            self.combo_repr.setCurrentText(str(repr_val).capitalize())

            self.row_ambient.set_value(r.get("ambient", 0.1))
            self.row_diffuse.set_value(r.get("diffuse", 0.7))
            self.row_specular.set_value(r.get("specular", 0.2))
            self.row_specular_pwr.set_value(r.get("specular_power", 10.0))
            self.check_edges.setChecked(r.get("edge_visibility", False))

        except Exception as e:
            logger.error(f"Erro ao atualizar UI a partir das propriedades: {e}")
        finally:
            self._is_loading_props = False

    def _save_property_change(self, property_name: str, value) -> None:
        if not hasattr(self, "object_properties") or not self.patient_path:
            return
        self._save_to_json()

    def _save_to_json(self) -> None:
        if not hasattr(self, "object_properties") or not self.patient_path:
            return
        json_path = self.patient_path / self.object_properties.file_path
        try:
            with open(json_path.with_suffix(".json"), "w", encoding="utf-8") as f:
                json.dump(self.object_properties.to_json(), f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar: {e}")


# ---------------------------------------------------------------------------
# Vec3SliderWidget
# ---------------------------------------------------------------------------

class Vec3SliderWidget(QtWidgets.QWidget):
    changed = QtCore.Signal(list)

    def __init__(self, min_val, max_val, defaults=(0, 0, 0), decimals=2, colors=None, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.rows = []
        colors = colors or ["#ff4b4b", "#4bff4b", "#4b4bff"]

        for lbl, color, d in zip(("X", "Y", "Z"), colors, defaults):
            row = AxisSliderRow(lbl, min_val, max_val, d, decimals=decimals, color=color)
            row.changed.connect(self._on_row_changed)
            layout.addWidget(row)
            self.rows.append(row)

    def _on_row_changed(self, _=None):
        self.changed.emit(self.get_values())

    def set_values(self, values):
        if len(values) != len(self.rows):
            return
        for r, v in zip(self.rows, values):
            r.set_value(v)

    def get_values(self):
        return [r.get_value() for r in self.rows]


# ---------------------------------------------------------------------------
# AxisSliderRow (Slider Atômico)
# ---------------------------------------------------------------------------

class AxisSliderRow(QtWidgets.QWidget):
    changed = QtCore.Signal(float)

    def __init__(self, label, min_val, max_val, default, decimals=2, color=None, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.prec = 10 ** decimals

        lbl_widget = QtWidgets.QLabel(label)
        if color:
            lbl_widget.setStyleSheet(f"colors: {color}; font-weight: bold;")

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.spinbox = QtWidgets.QDoubleSpinBox()

        self.slider.setRange(int(min_val * self.prec), int(max_val * self.prec))
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setDecimals(decimals)
        self.spinbox.setSingleStep(1.0 / self.prec)

        layout.addWidget(lbl_widget)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)

        self.set_value(default)

    def _on_slider_changed(self, value):
        val = value / self.prec
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(val)
        self.spinbox.blockSignals(False)
        self.changed.emit(val)

    def _on_spinbox_changed(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(int(value * self.prec))
        self.slider.blockSignals(False)
        self.changed.emit(value)

    def set_value(self, value):
        self.blockSignals(True)
        self.spinbox.setValue(value)
        self.slider.setValue(int(value * self.prec))
        self.blockSignals(False)

    def get_value(self):
        return self.spinbox.value()


if __name__ == "__main__":
    from dataclasses import dataclass, field
    from unittest.mock import MagicMock

    @dataclass
    class FakeProps:
        id: str = "123"
        file_path: str = "object_123.json"
        opacity: float = 0.8
        transform: dict = field(default_factory=lambda: {
            "position": [10.0, 20.0, 30.0],
            "rotation": [0.0, 45.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
        })
        render: dict = field(default_factory=lambda: {
            "colors": [0.2, 0.6, 1.0],
            "representation": "surface",
            "ambient": 0.2,
            "diffuse": 0.8,
            "specular": 0.5,
            "specular_power": 25.0,
            "edge_visibility": True,
        })

        def to_json(self):
            return {
                "id": self.id,
                "file_path": self.file_path,
                "opacity": self.opacity,
                "transform": self.transform,
                "render": self.render
            }

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("OpenCMF — Properties Editor")
    win.resize(400, 860)

    mock_context = MagicMock()
    mock_context.event_bus = MagicMock()
    mock_context.scene_manager = MagicMock()
    mock_context.tool_manager = MagicMock()

    comp = ObjectProperties_SidePanel(
        context=mock_context,
        title=""
    )

    fake_props = FakeProps()
    comp.object_properties = fake_props
    comp.patient_path = Path("./teste")

    comp.current_object_id = "123"
    comp.current_object_name = "Objeto Teste"

    comp.load_from_props(fake_props)

    scroll = QtWidgets.QScrollArea()
    scroll.setWidget(comp)
    scroll.setWidgetResizable(True)
    win.setCentralWidget(scroll)
    win.show()

    sys.exit(app.exec())