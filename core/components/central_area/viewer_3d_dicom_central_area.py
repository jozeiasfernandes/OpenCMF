'''
Usuário move o Slider -> Viewer3D_Dicom_Widget_CentralArea emite OBJECT_UPDATED.SceneBridge escuta o evento.  SceneBridge solicita a atualização ao VTKPropertySync ou ActorFactory.  VTKSceneRenderer realiza o refresh() final.

'''

from PySide6 import QtWidgets, QtCore

from core.components.bases.base_central_area import CentralAreaBase
from core.scene.events.scene_events import SceneEvents


class Viewer3D_Dicom_Widget_CentralArea(CentralAreaBase):
    def __init__(self, titulo: str, cor: str, event_bus, viewer_registry, parent=None):
        super().__init__(titulo, cor, parent)
        self.event_bus = event_bus
        self.viewer_registry = viewer_registry
        self.is_maximized = False

        self.viewer_registry.register(titulo, self)

        self._setup_ui()
        self.vtkWidget.installEventFilter(self)

    def eventFilter(self, source, event):
        if source is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() == QtCore.Qt.LeftButton:
                self._toggle_maximize()
                return True
        return super().eventFilter(source, event)

    def _setup_ui(self):
        self.combo_presets = QtWidgets.QComboBox()
        self.combo_presets.setFixedWidth(120)
        self.combo_presets.currentTextChanged.connect(
            lambda t: self.event_bus.emit(SceneEvents.OBJECT_UPDATED, preset=t)
        )

        self.slider_threshold = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_threshold.setRange(-1000, 3000)
        self.slider_threshold.setValue(400)
        self.slider_threshold.valueChanged.connect(self._on_threshold_changed)

        self.lbl_value = QtWidgets.QLabel("400 HU")
        self.lbl_value.setFixedWidth(60)

        self.btn_maximize = QtWidgets.QPushButton("Max")
        self.btn_maximize.setFixedSize(24, 24)
        self.btn_maximize.clicked.connect(self._toggle_maximize)

        self.adicionar_controle(self.combo_presets)
        self.adicionar_controle(self.slider_threshold)
        self.adicionar_controle(self.lbl_value)
        self.adicionar_controle(self.btn_maximize)

    def set_presets(self, preset_list: list):
        self.combo_presets.clear()
        self.combo_presets.addItems(sorted(preset_list))

    def _on_threshold_changed(self, value: int):
        self.lbl_value.setText(f"{value} HU")
        self.event_bus.emit(
            SceneEvents.OBJECT_UPDATED,
            property="threshold",
            value=value
        )

    def _toggle_maximize(self):
        self.is_maximized = not self.is_maximized
        self.event_bus.emit(
            SceneEvents.INTERACTION_MODE_CHANGED,
            maximized=self.is_maximized
        )