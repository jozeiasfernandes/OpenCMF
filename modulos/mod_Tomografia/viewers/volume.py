from .base import JanelaBase
from PySide6 import QtCore

class Janela3D(JanelaBase):
    thresholdChanged = QtCore.Signal(int)

    def __init__(self, nome: str, parent=None):
        super().__init__(nome, parent)
        self.indicator.setText("3D - Volume")
        self.slider.setRange(0, 3000)
        self.slider.setValue(200)
        self.slider.show()
        self.slider.valueChanged.connect(self.thresholdChanged.emit)