from PySide6 import QtWidgets, QtCore
from typing import Optional
from modules.mod_patients.ui_components import criar_linha_arquivo
from core.components.bases.base_sidepanel import BaseSidePanel
from core.scene.scene_manager import SceneManager
from core.scene.events.scene_events import SceneEvents


class SegmentacaoSidePanel(BaseSidePanel):
    pathChanged = QtCore.Signal(str)
    thresholdChanged = QtCore.Signal(int)

    side_panel_name = "Segmentação de Volumes"

    def setup_ui(self) -> None:
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        group_arq = QtWidgets.QGroupBox("Fonte de Dados")
        lay_arq = QtWidgets.QVBoxLayout(group_arq)
        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_tomografia.setPlaceholderText("Caminho da pasta DICOM...")

        def abrir_seletor():
            caminho = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecionar Pasta DICOM")
            if caminho:
                self.edit_tomografia.setText(caminho)
                self.pathChanged.emit(caminho)
                if self.has_scene:
                    self.scene_manager.import_and_add(caminho, category="dicom")

        lay_arq.addWidget(criar_linha_arquivo(self.edit_tomografia, abrir_seletor, True))
        self.layout.addWidget(group_arq)

        group_config = QtWidgets.QGroupBox("Configurações da malha")
        grid_layout = QtWidgets.QGridLayout(group_config)
        self.slider_hu = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_hu.setRange(-1000, 3000)
        self.slider_hu.setValue(226)
        self.slider_hu.valueChanged.connect(self._on_slider_moved)

        self.lbl_hu_value = QtWidgets.QLabel("226 HU")
        grid_layout.addWidget(QtWidgets.QLabel("Densidade:"), 0, 0)
        grid_layout.addWidget(self.slider_hu, 0, 1)
        grid_layout.addWidget(self.lbl_hu_value, 0, 2)
        self.layout.addWidget(group_config)

        self.btn_preview = QtWidgets.QPushButton(" Gerar Máscara")
        self.btn_preview.clicked.connect(self._solicitar_mascara)
        self.layout.addWidget(self.btn_preview)

        self.layout.addStretch()

        self.btn_stl = QtWidgets.QPushButton(" Exportar STL")
        self.btn_stl.clicked.connect(self._solicitar_exportar)
        self.layout.addWidget(self.btn_stl)

    def _solicitar_mascara(self):
        target_id = self.scene_manager.selection.get_first_selected() if self.has_scene else None
        if self.event_bus:
            self.event_bus.emit(SceneEvents.INTERACTION_MODE_CHANGED, mode="SEGMENTATION", target=target_id)
        print(f"Modo de segmentação solicitado para o objeto: {target_id}")

    def _solicitar_exportar(self):
        if self.has_scene:
            selected = self.scene_manager.selection.selected_ids
            print(f"Exportando IDs selecionados da cena: {selected}")

    def _on_slider_moved(self, valor):
        self.lbl_hu_value.setText(f"{valor} HU")
        self.thresholdChanged.emit(valor)
        if self.event_bus and self.has_scene:
            target_id = self.scene_manager.selection.get_first_selected()
            self.event_bus.emit(SceneEvents.OBJECT_UPDATED, object_id=target_id, property="threshold", value=valor)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    window = QtWidgets.QMainWindow()
    window.setWindowTitle(f"OpenCMF - Teste {SegmentacaoSidePanel.side_panel_name}")
    window.resize(400, 500)

    widget = SegmentacaoSidePanel(scene_manager=None)

    def on_path_changed(caminho):
        print(f"Caminho alterado: {caminho}")

    def on_threshold_changed(valor):
        print(f"Threshold alterado: {valor}")

    widget.pathChanged.connect(on_path_changed)
    widget.thresholdChanged.connect(on_threshold_changed)

    window.setCentralWidget(widget)
    window.show()

    sys.exit(app.exec())