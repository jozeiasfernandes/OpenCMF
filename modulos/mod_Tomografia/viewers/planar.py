from PySide6 import QtWidgets, QtCore, QtGui
from .base import JanelaBase


class Janela2D(JanelaBase):
    # Sinal emitido quando o slider de navegação de fatias é movido
    sliceChanged = QtCore.Signal(int)

    def __init__(self, nome: str, parent=None):
        # Inicializa a base (que cria o vtkWidget, indicator, etc)
        super().__init__(nome, parent)

        # Layout para organizar o widget VTK e o Slider
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Adiciona o widget VTK (já configurado na JanelaBase)
        layout.addWidget(self.vtkWidget, stretch=1)

        # Slider de navegação de fatias (específico das janelas 2D)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setStyleSheet("""
            QSlider::handle:horizontal {
                background: #3ea6fa;
                width: 14px;
                border-radius: 7px;
            }
        """)

        # Conecta o slider ao sinal
        self.slider.valueChanged.connect(self.sliceChanged.emit)

        layout.addWidget(self.slider)

    def _vtk_wheel_event(self, interactor, event):
        """Sobrescreve o scroll da base para navegar nas fatias via mouse."""
        delta = 1 if event == "MouseWheelForwardEvent" else -1
        novo_valor = self.slider.value() + delta
        self.slider.setValue(novo_valor)