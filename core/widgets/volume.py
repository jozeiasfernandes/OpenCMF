from modulos.mod_Tomografia.viewers.base import JanelaBase
from PySide6 import QtWidgets, QtCore


class Janela3D(JanelaBase):
    thresholdChanged = QtCore.Signal(int)

    def __init__(self, nome: str, parent=None):
        # MUITO IMPORTANTE: Chama o init da base para criar o vtkWidget e o indicator
        super().__init__(nome, parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Adiciona o visualizador (vtkWidget vem da JanelaBase)
        layout.addWidget(self.vtkWidget)

        # 2. Configura o indicador de texto (já existe na JanelaBase)
        self.indicator.setText("Visualização 3D")

        # 3. Adiciona controles de Threshold (específicos do 3D)
        controles = QtWidgets.QWidget()
        ctrl_layout = QtWidgets.QHBoxLayout(controles)

        label = QtWidgets.QLabel("Threshold:")
        label.setStyleSheet("color: white; font-size: 10px;")

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 2000)
        self.slider.setValue(200)
        self.slider.setFixedHeight(20)
        self.slider.valueChanged.connect(self.thresholdChanged.emit)

        ctrl_layout.addWidget(label)
        ctrl_layout.addWidget(self.slider)

        layout.addWidget(controles)