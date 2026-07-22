from PySide6 import QtWidgets
from core import tr


class TabToolbar(QtWidgets.QWidget):
    """Aba de configurações para a Toolbar."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.lbl_title = QtWidgets.QLabel(tr("configs.toolbar", "Configurações da Toolbar"))
        layout.addWidget(self.lbl_title)

        self.checkbox_visibilidade = QtWidgets.QCheckBox(
            tr("configs.toolbar.show_by_default", "Mostrar Toolbar por padrão")
        )
        self.checkbox_visibilidade.setChecked(True)
        layout.addWidget(self.checkbox_visibilidade)

        layout.addStretch()