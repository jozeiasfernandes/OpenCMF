import os
from PySide6 import QtWidgets, QtCore, QtGui
from core.volume.lookup_table.lut_presets import LUTPresets


class LUTDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        name = index.data()
        stops = LUTPresets.PRESETS.get(name, [])
        rect = option.rect

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(rect, option.palette.highlight())

        gradient = QtGui.QLinearGradient(rect.left() + 5, 0, rect.right() - 5, 0)
        for pos, hex_val in stops:
            gradient.setColorAt(pos, QtGui.QColor(hex_val))

        grad_rect = rect.adjusted(5, 4, -5, -4)
        painter.setBrush(gradient)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(grad_rect, 3, 3)

        painter.setPen(QtGui.QColor(0, 0, 0, 160))
        painter.drawText(rect.adjusted(1, 1, 1, 1), QtCore.Qt.AlignCenter, name)
        painter.setPen(QtCore.Qt.white)
        painter.drawText(rect, QtCore.Qt.AlignCenter, name)

        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(100, 28)


class VolumeViewerToolbar(QtWidgets.QToolBar):
    layoutChanged = QtCore.Signal(str)
    lutChanged = QtCore.Signal(str)

    def __init__(self, path_icones: str, parent=None):
        super().__init__(parent)
        self.path_icones = path_icones
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(38)
        self.setMovable(False)
        self.setStyleSheet("""
            QToolBar { 
                background: #1E1E1E; 
                border-bottom: 1px solid #333; 
                spacing: 12px; 
                padding: 0px 10px; 
            } 
            QComboBox { 
                background: #333; 
                color: white; 
                border: 1px solid #444; 
                border-radius: 3px;
                padding: 2px 5px; 
                min-width: 130px; 
            }
            QComboBox::drop-down { border: none; }
            QLabel { 
                color: #888; 
                font-size: 10px; 
                font-weight: bold; 
                text-transform: uppercase;
            }
        """)

        self.addWidget(QtWidgets.QLabel("Layout"))
        self.combo_layout = QtWidgets.QComboBox()
        self._populate_layouts()
        self.combo_layout.currentTextChanged.connect(self.layoutChanged.emit)
        self.addWidget(self.combo_layout)

        self.addSeparator()

        self.addWidget(QtWidgets.QLabel("Color Map"))
        self.combo_lut = QtWidgets.QComboBox()
        self.combo_lut.setItemDelegate(LUTDelegate(self.combo_lut))
        self.combo_lut.addItems(list(LUTPresets.PRESETS.keys()))
        self.combo_lut.currentTextChanged.connect(self.lutChanged.emit)
        self.addWidget(self.combo_lut)

    def _populate_layouts(self):
        opcoes = [
            ("4 Quadrantes", "4_janelas.png"),
            ("3D Destacado", "3_1.png"),
            ("Apenas 3D", "3D.png"),
            ("Axial", "axial.png"),
            ("Sagital", "sagital.png"),
            ("Coronal", "coronal.png")
        ]
        for nome, img in opcoes:
            path = os.path.join(self.path_icones, img)
            icon = QtGui.QIcon(path) if os.path.exists(path) else QtGui.QIcon()
            self.combo_layout.addItem(icon, nome)

    def set_lut_text(self, lut_name: str):
        self.combo_lut.blockSignals(True)
        self.combo_lut.setCurrentText(lut_name)
        self.combo_lut.blockSignals(False)

    def set_layout_text(self, layout_name: str):
        self.combo_layout.blockSignals(True)
        self.combo_layout.setCurrentText(layout_name)
        self.combo_layout.blockSignals(False)