from typing import Optional, Any
import sys
import json
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
from core.color import ColorPickerWidget
from core.components.bases.base_sidepanel import BaseSidePanel


# ---------------------------------------------------------------------------
# ObjectProperties_SidePanel (Painel Principal — Mantido no topo)
# ---------------------------------------------------------------------------

class ObjectProperties_SidePanel(BaseSidePanel):
    side_panel_name = "Propriedades do Objeto"
    toolbox_name = "Propriedades"

    def __init__(self, context: Any, titulo: str = "Propriedades", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, titulo=titulo, parent=parent)
        self.current_object_id = None
        self.current_object_name = None
        self.patient_path = None
        self.object_properties = None
        self._is_loading_props = False

        # Configurar UI
        self.setup_ui()

    def setup_ui(self) -> None:
        """Configura a interface usando o layout herdado de BaseSidePanel."""
        self.layout.setContentsMargins(5, 5, 5, 5)
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
        self.color_picker.colorChanged.connect(lambda c: self._dispatch("color", c))
        lay_a.addRow("Cor:", self.color_picker)

        self.row_opacity = AxisSliderRow("", 0.0, 1.0, 1.0)
        self.row_opacity.changed.connect(lambda v: self._dispatch("opacity", v))
        lay_a.addRow("Opacidade:", self.row_opacity)

        self.combo_repr = QtWidgets.QComboBox()
        self.combo_repr.addItems(["Surface", "Wireframe", "Points"])
        self.combo_repr.currentTextChanged.connect(lambda t: self._dispatch("representation", t))
        lay_a.addRow("Representação:", self.combo_repr)

        self.row_ambient = AxisSliderRow("", 0.0, 1.0, 0.1)
        self.row_ambient.changed.connect(lambda v: self._dispatch("ambient", v))
        lay_a.addRow("Ambiente:", self.row_ambient)

        self.row_diffuse = AxisSliderRow("", 0.0, 1.0, 0.7)
        self.row_diffuse.changed.connect(lambda v: self._dispatch("diffuse", v))
        lay_a.addRow("Difuso:", self.row_diffuse)

        self.row_specular = AxisSliderRow("", 0.0, 1.0, 0.2)
        self.row_specular.changed.connect(lambda v: self._dispatch("specular", v))
        lay_a.addRow("Especular:", self.row_specular)

        self.row_specular_pwr = AxisSliderRow("", 1.0, 128.0, 10.0, decimals=1)
        self.row_specular_pwr.changed.connect(lambda v: self._dispatch("specular_power", v))
        lay_a.addRow("Brilho:", self.row_specular_pwr)

        self.check_edges = QtWidgets.QCheckBox("Mostrar Arestas")
        self.check_edges.toggled.connect(lambda v: self._dispatch("edge_visibility", v))
        lay_a.addRow("", self.check_edges)

        self.layout.addWidget(group_a)
        self.layout.addStretch()

    def _dispatch(self, property_name: str, value) -> None:
        """Centraliza o salvamento e a comunicação via EventBus."""
        if self._is_loading_props:
            return

        # 1. Salvar alteração (lógica original)
        self._save_property_change(property_name, value)

        # 2. Emitir evento centralizado (Arquitetura Base)
        if self.event_bus:
            self.event_bus.emit(f"object_{property_name}_changed", {
                "object": self.current_object_name,
                "value": value
            })

    def load_from_props(self, props) -> None:
        self._is_loading_props = True
        t = props.transform if isinstance(props.transform, dict) else vars(props.transform)
        r = props.render if isinstance(props.render, dict) else vars(props.render)

        self.vec_pos.set_values(t.get("position", [0, 0, 0]))
        self.vec_rot.set_values(t.get("rotation", [0, 0, 0]))
        self.vec_scl.set_values(t.get("scale", [1, 1, 1]))
        self.color_picker.set_rgb(r.get("color", [1, 1, 1]))
        self.row_opacity.set_value(getattr(props, "opacity", 1.0))
        self.combo_repr.setCurrentText(r.get("representation", "surface").capitalize())
        self.row_ambient.set_value(r.get("ambient", 0.1))
        self.row_diffuse.set_value(r.get("diffuse", 0.7))
        self.row_specular.set_value(r.get("specular", 0.2))
        self.row_specular_pwr.set_value(r.get("specular_power", 10.0))
        self.check_edges.setChecked(r.get("edge_visibility", False))
        self._is_loading_props = False

    def _save_property_change(self, property_name: str, value) -> None:
        if not self.object_properties or not self.patient_path:
            return
        # Lógica de atualização interna...
        self._save_to_json()

    def _save_to_json(self) -> None:
        if not self.object_properties or not self.patient_path:
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
            row.changed.connect(lambda _: self.changed.emit(self.get_values()))
            layout.addWidget(row)
            self.rows.append(row)

    def set_values(self, values):
        for r, v in zip(self.rows, values): r.set_value(v)

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

        # CORREÇÃO AQUI: Armazene como atributo da instância
        self.prec = 10 ** decimals

        # Inicialize seus widgets (exemplo básico)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.spinbox = QtWidgets.QDoubleSpinBox()

        # Configure min/max do slider com base na precisão
        self.slider.setRange(int(min_val * self.prec), int(max_val * self.prec))

        layout.addWidget(QtWidgets.QLabel(label))
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)

    def set_value(self, value):
        """Atualiza o valor do slider e do spinbox."""
        self.slider.blockSignals(True)
        self.spinbox.blockSignals(True)

        # Agora self.prec será encontrado corretamente
        self.spinbox.setValue(value)
        self.slider.setValue(int(value * self.prec))

        self.slider.blockSignals(False)
        self.spinbox.blockSignals(False)


if __name__ == "__main__":
    from dataclasses import dataclass, field


    @dataclass
    class FakeProps:
        id: str = "123"
        file_path: str = "object_123.json"
        opacity: float = 0.8
        transform: dict = field(default_factory=lambda: {
            "position": [10, 20, 30],
            "rotation": [0, 45, 0],
            "scale": [1, 1, 1],
        })
        render: dict = field(default_factory=lambda: {
            "color": [0.2, 0.6, 1.0],
            "representation": "surface",
            "ambient": 0.2,
            "diffuse": 0.8,
            "specular": 0.5,
            "specular_power": 25.0,
            "edge_visibility": True,
        })

        def to_json(self):
            return self.__dict__


    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Configuração de paleta mantida...
    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window, QtGui.QColor(40, 40, 40))
    pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(220, 220, 220))
    pal.setColor(QtGui.QPalette.Base, QtGui.QColor(30, 30, 30))
    pal.setColor(QtGui.QPalette.Text, QtGui.QColor(220, 220, 220))
    pal.setColor(QtGui.QPalette.Button, QtGui.QColor(55, 55, 55))
    pal.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(220, 220, 220))
    pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(80, 120, 200))
    pal.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    app.setPalette(pal)

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("OpenCMF — Properties Editor")
    win.resize(400, 860)

    # CORRIGIDO: Passar context e titulo
    comp = ObjectProperties_SidePanel(
        context=None,  # Ou passe um SceneManager se disponível
        titulo="Propriedades",
        parent=None
    )

    # Criar um objeto FakeProps para teste
    fake_props = FakeProps()
    comp.object_properties = fake_props
    comp.patient_path = Path("./teste")
    comp.load_from_props(fake_props)

    scroll = QtWidgets.QScrollArea()
    scroll.setWidget(comp)
    scroll.setWidgetResizable(True)
    win.setCentralWidget(scroll)
    win.show()
    sys.exit(app.exec())

