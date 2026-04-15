from PySide6 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class JanelaBase(QtWidgets.QWidget):
    def __init__(self, titulo, cor_identificacao, parent=None):
        super().__init__(parent)
        self.titulo = titulo
        self.cor_id = cor_identificacao
        self._setup_base_ui()

    def _setup_base_ui(self):
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(1, 1, 1, 1)
        self.layout_principal.setSpacing(0)

        self.vtkWidget = QVTKRenderWindowInteractor(self)

        self.indicator = QtWidgets.QLabel(self.titulo, self.vtkWidget)
        self.indicator.setStyleSheet(f"""
            color: {self.cor_id}; 
            background: rgba(0, 0, 0, 180); 
            font-weight: bold; 
            padding: 4px 8px;
            border-radius: 2px;
            font-size: 11px;
        """)
        self.indicator.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.indicator.move(5, 5)

        self.barra_inferior = QtWidgets.QFrame()
        self.barra_inferior.setFixedHeight(42)
        self.barra_inferior.setStyleSheet(f"""
            QFrame {{ background-color: #1A1A1A; border-top: 1px solid #333; border-left: 4px solid {self.cor_id}; }}
            QLabel {{ color: #EEE; font-size: 11px; font-weight: bold; }}
            QToolButton {{ background: #333; color: white; border-radius: 2px; padding: 2px; }}
        """)

        self.layout_barra = QtWidgets.QHBoxLayout(self.barra_inferior)
        self.layout_barra.setContentsMargins(8, 0, 8, 0)

        self.layout_principal.addWidget(self.vtkWidget, stretch=1)
        self.layout_principal.addWidget(self.barra_inferior)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'indicator'):
            self.indicator.move(5, 5)

    def adicionar_controle(self, widget):
        self.layout_barra.addWidget(widget)