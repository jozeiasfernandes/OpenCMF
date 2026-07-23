from PySide6 import QtWidgets, QtCore
from typing import Optional, Any
from modules.mod_patients.ui_components import criar_linha_arquivo
from core.components.bases.base_sidepanel import BaseSidePanel


class Segmentation_SidePanel(BaseSidePanel):
    pathChanged = QtCore.Signal(str)
    thresholdChanged = QtCore.Signal(int)
    solicitarMascara = QtCore.Signal()
    solicitarExportarSTL = QtCore.Signal()

    side_panel_name = "Segmentação de Volumes"

    def __init__(self, context: Any, parent: Optional[QtWidgets.QWidget] = None, **kwargs):
        super().__init__(context=context, title="", parent=parent)

    def setup_ui(self) -> None:


        self.layout.setSpacing(10)
        self.layout.setContentsMargins(5, 5, 5, 5)

        group_arq = QtWidgets.QGroupBox("Fonte de Dados")
        lay_arq = QtWidgets.QVBoxLayout(group_arq)

        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_tomografia.setPlaceholderText("Caminho da pasta DICOM...")

        self.edit_tomografia.textChanged.connect(self.pathChanged.emit)

        def abrir_seletor():
            p = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecionar Pasta DICOM")
            if p:
                self.edit_tomografia.setText(p)

        lay_arq.addWidget(criar_linha_arquivo(self.edit_tomografia, abrir_seletor, True))
        self.layout.addWidget(group_arq)

        # GroupBox: Configurações
        group_config = QtWidgets.QGroupBox("Configurações da malha")
        grid_layout = QtWidgets.QGridLayout(group_config)
        grid_layout.setSpacing(10)

        lbl_densidade = QtWidgets.QLabel("Filtro de Densidade:")
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

        lbl_resolucao = QtWidgets.QLabel("Resolução:")
        self.combo_qualidade = QtWidgets.QComboBox()
        self.combo_qualidade.addItems(["Alta", "Média", "Baixa"])
        self.combo_qualidade.setCurrentIndex(1)

        grid_layout.addWidget(lbl_resolucao, 1, 0)
        grid_layout.addWidget(self.combo_qualidade, 1, 1, 1, 2)

        self.layout.addWidget(group_config)

        # Botão Gerar Máscara
        self.btn_preview = QtWidgets.QPushButton(" Gerar Máscara")
        self.btn_preview.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        self.btn_preview.setMinimumHeight(35)
        self.btn_preview.clicked.connect(self.solicitarMascara.emit)
        self.layout.addWidget(self.btn_preview)

        # Espaçador
        self.layout.addStretch()

        # Botão Exportar STL
        self.btn_stl = QtWidgets.QPushButton(" Exportar STL")
        self.btn_stl.setMinimumHeight(45)
        self.btn_stl.setStyleSheet("""
            QPushButton {
                background-color: #2d5a27; 
                color: white; 
                font-weight: bold; 
                font-size: 13px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a7532;
            }
            QPushButton:pressed {
                background-color: #1e3d1a;
            }
        """)
        self.btn_stl.clicked.connect(self.solicitarExportarSTL.emit)
        self.layout.addWidget(self.btn_stl)

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()
            else:
                self._clear_layout_recursive(item.layout())

    def clear_layout_recursive(self, layout):
        """Remove recursivamente widgets de sub-layouts."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout_recursive(item.layout())

    def _on_slider_moved(self, val):
        self.lbl_hu_value.setText(f"{val} HU")
        self.thresholdChanged.emit(val)

    def set_path(self, caminho: str):
        self.edit_tomografia.blockSignals(True)
        self.edit_tomografia.setText(caminho)
        self.edit_tomografia.blockSignals(False)

    def get_value(self) -> int:
        return self.slider_hu.value()

    def get_qualidade_index(self) -> int:
        return self.combo_qualidade.currentIndex()


Component = Segmentation_SidePanel

if __name__ == "__main__":
    import sys
    from unittest.mock import MagicMock
    from core.components.bases.base_toolbar import AppContext
    from core.components.bases.base_tool.tool_manager import ToolManager
    from core.scene.events.event_bus import EventBus

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Criação do contexto completo satisfazendo os contratos da arquitetura base
    context = AppContext(
        scene_manager=MagicMock(),
        tool_manager=ToolManager(),
        event_bus=EventBus()
    )

    # Criar janela principal
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("OpenCMF - Teste Segmentation Toolbox")
    window.resize(400, 500)

    widget = Segmentation_SidePanel(context)

    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(widget)

    # Definir o scroll como widget central
    window.setCentralWidget(scroll)

    # Conexões de Sinais
    widget.pathChanged.connect(lambda path: print(f"Caminho alterado: {path}"))
    widget.thresholdChanged.connect(lambda val: print(f"Threshold alterado: {val}"))
    widget.solicitarMascara.connect(lambda: print("Solicitando geração de máscara"))
    widget.solicitarExportarSTL.connect(lambda: print("Solicitando exportação STL"))

    window.show()
    sys.exit(app.exec())