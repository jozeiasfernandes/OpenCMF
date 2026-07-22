from PySide6 import QtWidgets


class Tab2DViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Placeholder para configurações 2D (MPR)
        self.lbl_title = QtWidgets.QLabel("Configurações do Visualizador 2D")
        layout.addWidget(self.lbl_title)
        layout.addStretch()