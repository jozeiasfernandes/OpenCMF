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
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        self.vtkWidget = QVTKRenderWindowInteractor(self)

        self.indicator = QtWidgets.QLabel(self.titulo, self.vtkWidget)
        self.indicator.setStyleSheet(f"""
            color: {self.cor_id}; 
            background: rgba(0, 0, 0, 180); 
            font-weight: bold; 
            padding: 0px 2px;
            border-radius: 1px;
            font-size: 11px;
        """)
        self.indicator.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.indicator.move(0, 0)

        self.barra_inferior = QtWidgets.QFrame()
        self.barra_inferior.setFixedHeight(30)
        self.barra_inferior.setStyleSheet(f"""
            QFrame {{ background-color: #1A1A1A; border-top: 0px solid #333; border-left: 2px solid {self.cor_id}; }}
            QLabel {{ color: #EEE; font-size: 11px;}}
            QToolButton {{ background: #333; color: white; border-radius: 2px; padding: 0px; }}
            QComboBox {{ font-size: 11px; border: 0px; border-radius: 1px; padding: 1px 1px 1px 4px;}}
        """)

        self.layout_barra = QtWidgets.QHBoxLayout(self.barra_inferior)
        self.layout_barra.setContentsMargins(4, 0, 4, 0)

        self.layout_principal.addWidget(self.vtkWidget, stretch=1)
        self.layout_principal.addWidget(self.barra_inferior)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'indicator'):
            self.indicator.move(0, 0)

    def adicionar_controle(self, widget):
        self.layout_barra.addWidget(widget)