from .base import JanelaBase
from PySide6 import QtCore

class Janela2D(JanelaBase):
    sliceChanged = QtCore.Signal(int)

    def __init__(self, nome: str, parent=None):
        super().__init__(nome, parent)
        self.slider.valueChanged.connect(self.sliceChanged.emit)
        self.slider.show()