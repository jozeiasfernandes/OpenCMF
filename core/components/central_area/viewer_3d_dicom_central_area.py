'''
Usuário move o Slider -> Viewer3D_Dicom_Widget_CentralArea emite OBJECT_UPDATED.SceneBridge escuta o evento.  SceneBridge solicita a atualização ao VTKPropertySync ou ActorFactory.  VTKSceneRenderer realiza o refresh() final.

'''

import os
from PySide6 import QtWidgets, QtCore, QtGui

from core.components.bases.base_central_area import CentralAreaBase
from core.scene.events.scene_events import SceneEvents


class Viewer3D_Dicom_Widget_CentralArea(CentralAreaBase):
    maximizeRequested = QtCore.Signal(bool)
    thresholdChanged = QtCore.Signal(int)
    viewChanged = QtCore.Signal(str)
    presetChanged = QtCore.Signal(str)

    def __init__(self, context, title: str, cor: str, event_bus, viewer_registry, parent=None):
        if not hasattr(context, 'scene_manager'):
            raise AttributeError(
                f"O objeto context passado para {title} deve possuir o atributo 'scene_manager'. "
                f"Context recebido: {type(context)}"
            )

        super().__init__(context=context, title=title, cor_identificacao=cor, parent=parent)

        self.id = title.replace(" ", "_").lower()

        self._event_bus = None
        self.event_bus = event_bus
        self.viewer_registry = viewer_registry

        self.viewer_registry.register(self)

        from pathlib import Path
        base_dir = Path(__file__).resolve().parent
        self.path_icons = base_dir.parent.parent.parent / "icons"

        self.setup_component()

        if hasattr(self, 'vtkWidget') and self.vtkWidget is not None:
            self.vtkWidget.installEventFilter(self)
        else:
            raise RuntimeError("Viewer3D: O vtkWidget não foi criado. Verifique a CentralAreaBase!")

    def setup_component(self):
        super().setup_component()

    def eventFilter(self, source, event):
        if source is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() == QtCore.Qt.LeftButton:
                self._toggle_maximize()
                return True
        return super().eventFilter(source, event)

    def setup_ui(self):
        """Configura a UI específica para visualização 3D."""
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

        if hasattr(self, 'layout_principal') and self.layout_principal:
            controls_layout = QtWidgets.QHBoxLayout()
            controls_layout.addWidget(self.combo_presets)
            controls_layout.addWidget(self.slider_threshold)
            controls_layout.addWidget(self.lbl_value)
            controls_layout.addWidget(self.btn_maximize)
            controls_layout.addStretch()

            self.layout_principal.addLayout(controls_layout)

            self.layout_principal.setContentsMargins(5, 5, 5, 5)
            self.layout_principal.setSpacing(10)

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

    def _update_maximize_icon(self):

        icon_name = "minimizar.png" if self.is_maximized else "maximizar.png"
        icon_path = os.path.join(self.path_icons, icon_name)
        if hasattr(self, 'btn_maximize') and os.path.exists(icon_path):
            self.btn_maximize.setIcon(QtGui.QIcon(icon_path))
            self.btn_maximize.setIconSize(QtCore.QSize(16, 16))

    @property
    def event_bus(self):
        return self._event_bus

    @event_bus.setter
    def event_bus(self, value):
        self._event_bus = value


if __name__ == "__main__":
    import sys
    from unittest.mock import MagicMock
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    mock_context = MagicMock()
    mock_event_bus = MagicMock()
    mock_viewer_registry = MagicMock()

    window = Viewer3D_Dicom_Widget_CentralArea(
        context=mock_context, # Adicionado aqui
        title="Teste DICOM Viewer",
        cor="#2c3e50",
        event_bus=mock_event_bus,
        viewer_registry=mock_viewer_registry
    )

    window.show()

    sys.exit(app.exec())