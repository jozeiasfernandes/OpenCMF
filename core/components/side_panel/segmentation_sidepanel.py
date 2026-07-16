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
        super().__init__(context, self.side_panel_name, parent)

    def setup_ui(self) -> None:
        """Configura a interface do usuário."""
        # O layout já existe e está disponível como self.layout
        # Limpa o layout caso já tenha widgets (por segurança)
        self.clear_layout()

        self.layout.setSpacing(10)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # GroupBox: Fonte de Dados
        group_arq = QtWidgets.QGroupBox("Fonte de Dados")
        lay_arq = QtWidgets.QVBoxLayout(group_arq)
        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_tomografia.setPlaceholderText("Caminho da pasta DICOM...")
        self.edit_tomografia.textChanged.connect(self.pathChanged.emit)

        def abrir_seletor():
            p = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecionar Pasta DICOM")
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
        """Remove todos os widgets do layout."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout_recursive(item.layout())

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


# Mantém o Component para compatibilidade com o sistema de plugins
Component = Segmentation_SidePanel

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")


    # Criar um contexto mock para teste
    class MockContext:
        scene_manager = None


    context = MockContext()

    # Criar um QMainWindow para hospedar o dock widget
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("OpenCMF - Teste Segmentation Toolbox")
    window.resize(400, 500)

    # Criar o widget como um dockable panel
    widget = Segmentation_SidePanel(context)

    # Adicionar como dock widget na janela principal
    window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, widget)


    def on_path_changed(path):
        print(f"Caminho alterado: {path}")


    def on_threshold_changed(value):
        print(f"Threshold alterado: {value}")


    def on_solicitar_mascara():
        print("Solicitando geração de máscara")


    def on_solicitar_exportar_stl():
        print("Solicitando exportação STL")


    widget.pathChanged.connect(on_path_changed)
    widget.thresholdChanged.connect(on_threshold_changed)
    widget.solicitarMascara.connect(on_solicitar_mascara)
    widget.solicitarExportarSTL.connect(on_solicitar_exportar_stl)

    window.show()

    sys.exit(app.exec())