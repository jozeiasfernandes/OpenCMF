from .base import JanelaBase
from PySide6 import QtCore, QtGui


class Janela2D(JanelaBase):
    sliceChanged = QtCore.Signal(int)
    windowLevelChanged = QtCore.Signal(float, float)  # Envia (Window, Level)

    def __init__(self, nome: str, parent=None):
        super().__init__(nome, parent)
        self.slider.valueChanged.connect(self.sliceChanged.emit)
        self.slider.show()

        self.ultimo_y = 0
        self.ultimo_x = 0
        self.window = 2000
        self.level = 400

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.ultimo_x = event.position().x()
            self.ultimo_y = event.position().y()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            dx = event.position().x() - self.ultimo_x
            dy = event.position().y() - self.ultimo_y

            # Sensibilidade do ajuste
            self.window += dx * 2
            self.level -= dy * 2

            self.window = max(1, self.window)  # Window não pode ser <= 0

            self.windowLevelChanged.emit(self.window, self.level)

            self.ultimo_x = event.position().x()
            self.ultimo_y = event.position().y()
        super().mouseMoveEvent(event)