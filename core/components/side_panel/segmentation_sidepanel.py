from __future__ import annotations
from typing import Any, Optional

from PySide6 import QtCore, QtWidgets

# Patient
from core.settings.paths.list_paths import PATIENTS_DIR

# Base
from core.components.bases.base_sidepanel import BaseSidePanel

# Localization
from core.settings.localization.translator import tr

#ui
from core.application.ui.create_file_row import create_file_row


class Segmentation_SidePanel(BaseSidePanel):
    pathChanged = QtCore.Signal(str)
    thresholdChanged = QtCore.Signal(int)
    requestMask = QtCore.Signal()
    solicitarExportarSTL = QtCore.Signal()

    side_panel_name = tr("modules.segmentation", "Segmentação de Volumes")

    def __init__(
        self,
        context: Any,
        parent: Optional[QtWidgets.QWidget] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(context=context, title="", parent=parent, **kwargs)

    # =========================================================================
    # UI SETUP & LAYOUT
    # =========================================================================
    def setup_ui(self) -> None:
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self._setup_source_group()
        self._setup_config_group()
        self._setup_actions()

    def _setup_source_group(self) -> None:
        group_arq = QtWidgets.QGroupBox(tr("import.panels.source", "Fonte de Dados"))
        lay_arq = QtWidgets.QVBoxLayout(group_arq)

        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_tomografia.setPlaceholderText(
            tr("dialogs.import.dicom", "Caminho da pasta DICOM...")
        )
        self.edit_tomografia.textChanged.connect(self.pathChanged.emit)

        def open_selector() -> None:
            initial_dir = str(PATIENTS_DIR) if PATIENTS_DIR.exists() else ""
            p = QtWidgets.QFileDialog.getExistingDirectory(
                self, tr("file_browser.select_directory_title", "Selecionar Pasta DICOM"), initial_dir
            )
            if p:
                self.edit_tomografia.setText(p)

        lay_arq.addWidget(create_file_row(self.edit_tomografia, open_selector, True))
        self.layout.addWidget(group_arq)

    def _setup_config_group(self) -> None:
        group_config = QtWidgets.QGroupBox(tr("configs.workspace", "Configurações da malha"))
        grid_layout = QtWidgets.QGridLayout(group_config)
        grid_layout.setSpacing(10)

        lbl_densidade = QtWidgets.QLabel(tr("modules.segmentation_density", "Filtro de Densidade:"))
        self.slider_hu = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_hu.setRange(-1000, 3000)
        self.slider_hu.setValue(226)
        self.slider_hu.valueChanged.connect(self._on_slider_moved)

        self.lbl_hu_value = QtWidgets.QLabel("226 HU")
        self.lbl_hu_value.setStyleSheet("font-weight: bold;")
        self.lbl_hu_value.setFixedWidth(60)

        grid_layout.addWidget(lbl_densidade, 0, 0)
        grid_layout.addWidget(self.slider_hu, 0, 1)
        grid_layout.addWidget(self.lbl_hu_value, 0, 2)

        lbl_resolucao = QtWidgets.QLabel(tr("modules.segmentation_resolution", "Resolução:"))
        self.combo_qualidade = QtWidgets.QComboBox()
        self.combo_qualidade.addItems([
            tr("modules.segmentation_high", "Alta"),
            tr("modules.segmentation_medium", "Média"),
            tr("modules.segmentation_low", "Baixa"),
        ])
        self.combo_qualidade.setCurrentIndex(1)

        grid_layout.addWidget(lbl_resolucao, 1, 0)
        grid_layout.addWidget(self.combo_qualidade, 1, 1, 1, 2)

        self.layout.addWidget(group_config)

    def _setup_actions(self) -> None:
        self.btn_preview = QtWidgets.QPushButton(
            tr("modules.segmentation_generate_mask", " Gerar Máscara")
        )
        self.btn_preview.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton)
        )
        self.btn_preview.setMinimumHeight(35)
        self.btn_preview.clicked.connect(self.requestMask.emit)
        self.layout.addWidget(self.btn_preview)

        self.layout.addStretch()

        self.btn_stl = QtWidgets.QPushButton(
            tr("modules.segmentation_export_stl", " Exportar STL")
        )
        self.btn_stl.setMinimumHeight(45)
        # Configurações estéticas fixas removidas para permitir controle via ThemeManager / QSS
        self.btn_stl.clicked.connect(self.solicitarExportarSTL.emit)
        self.layout.addWidget(self.btn_stl)

    # =========================================================================
    # PUBLIC METHODS (API & GETTERS/SETTERS)
    # =========================================================================
    def set_path(self, caminho: str) -> None:
        self.edit_tomografia.blockSignals(True)
        self.edit_tomografia.setText(caminho)
        self.edit_tomografia.blockSignals(False)

    def get_value(self) -> int:
        return self.slider_hu.value()

    def get_qualidade_index(self) -> int:
        return self.combo_qualidade.currentIndex()

    def clear_layout(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()
            else:
                self._clear_layout_recursive(item.layout())

    # =========================================================================
    # PRIVATE HELPERS & SLOTS
    # =========================================================================
    def _clear_layout_recursive(self, layout: QtWidgets.QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout_recursive(item.layout())

    def _on_slider_moved(self, val: int) -> None:
        self.lbl_hu_value.setText(f"{val} HU")
        self.thresholdChanged.emit(val)


Component = Segmentation_SidePanel

if __name__ == "__main__":
    import sys
    from unittest.mock import MagicMock
    from core.components.bases.base_component import AppContext
    from core.components.bases.base_tool.tool_manager import ToolManager
    from application.scene.events.event_bus import EventBus

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    context = AppContext(
        scene_manager=MagicMock(),
        tool_manager=ToolManager(),
        event_bus=EventBus(),
    )

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("OpenCMF - Teste Segmentation Toolbox")
    window.resize(400, 500)

    widget = Segmentation_SidePanel(context)

    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(widget)

    window.setCentralWidget(scroll)

    widget.pathChanged.connect(lambda path: print(f"Caminho alterado: {path}"))
    widget.thresholdChanged.connect(lambda val: print(f"Threshold alterado: {val}"))
    widget.requestMask.connect(lambda: print("Solicitando geração de máscara"))
    widget.solicitarExportarSTL.connect(lambda: print("Solicitando exportação STL"))

    window.show()
    sys.exit(app.exec())