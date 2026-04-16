from PySide6 import QtWidgets, QtCore
from pathlib import Path
from typing import Optional

class ObjetoManagerWidget(QtWidgets.QWidget):
    objetoToggled = QtCore.Signal(str, bool)
    requestRefresh = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemChanged.connect(self._handle_item_changed)

        self.btn_refresh = QtWidgets.QPushButton(" Atualizar Lista")
        self.btn_refresh.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))
        self.btn_refresh.clicked.connect(self.requestRefresh.emit)

        layout.addWidget(QtWidgets.QLabel("Gerenciar Visibilidade (3D):"))
        layout.addWidget(self.list_widget)
        layout.addWidget(self.btn_refresh)

    def _handle_item_changed(self, item):
        visivel = (item.checkState() == QtCore.Qt.Checked)
        self.objetoToggled.emit(item.text(), visivel)

    def atualizar_lista(self, pasta_stl: Optional[str] = None, incluir_volume: bool = True):
        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        if incluir_volume:
            item_vol = QtWidgets.QListWidgetItem("volume DICOM")
            item_vol.setFlags(item_vol.flags() | QtCore.Qt.ItemIsUserCheckable)
            item_vol.setCheckState(QtCore.Qt.Checked)
            self.list_widget.addItem(item_vol)

        if pasta_stl:
            caminho_stl = Path(pasta_stl)
            if caminho_stl.exists():
                for arquivo in caminho_stl.glob("*.stl"):
                    item = QtWidgets.QListWidgetItem(arquivo.name)
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
                    self.list_widget.addItem(item)

        self.list_widget.blockSignals(False)