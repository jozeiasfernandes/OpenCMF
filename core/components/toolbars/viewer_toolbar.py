import os
from PySide6 import QtWidgets, QtCore, QtGui
from core.volume.lookup_table.lut_presets import LUTPresets
from core.components.tools.color_map_tool import ColorMapTool
from core.components.tools.layout_dicom_tool import LayoutDicomTool


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

    def __init__(self, path_icones: str, color_map_tool: ColorMapTool = None, layout_tool: LayoutDicomTool = None,
                 parent=None):
        super().__init__(parent)
        self.path_icones = path_icones
        self.color_map_tool = color_map_tool
        self.layout_tool = layout_tool
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(38)
        self.setMovable(False)
        self.layout().setSpacing(12)
        self.layout().setContentsMargins(10, 0, 10, 0)

        self.addWidget(QtWidgets.QLabel("Layout"))
        self.combo_layout = QtWidgets.QComboBox()
        self.combo_layout.setFixedWidth(130)
        self._populate_layouts()
        self.combo_layout.currentTextChanged.connect(self._on_layout_changed)
        self.addWidget(self.combo_layout)

        self.addSeparator()

        self.addWidget(QtWidgets.QLabel("Color Map"))
        self.combo_lut = QtWidgets.QComboBox()
        self.combo_lut.setFixedWidth(130)
        self.combo_lut.setItemDelegate(LUTDelegate(self.combo_lut))
        self.combo_lut.addItems(list(LUTPresets.PRESETS.keys()))
        self.combo_lut.currentTextChanged.connect(self._on_lut_changed)
        self.addWidget(self.combo_lut)

    def update_tool_status(self):
        has_context = self.layout_tool is not None and self.layout_tool.context is not None
        self.combo_layout.setEnabled(has_context)

    def _on_layout_changed(self, name: str):
        if self.layout_tool and self.layout_tool.context:
            self.layout_tool.apply_layout(name)
        else:
            print(f"Aviso: Layout '{name}' solicitado, mas a ferramenta não está no contexto.")
            self.layoutChanged.emit(name)

    def _on_lut_changed(self, name: str):
        if self.color_map_tool:
            self.color_map_tool.apply_lut(name)

    def _populate_layouts(self):
        opcoes = [
            ("4 Quadrantes", "4_janelas.png"),
            ("3D Destacado", "3_1.png"),
            ("Apenas 3D", "3D.png"),
            ("Axial", "axial.png"),
            ("Sagital", "sagital.png"),
            ("Coronal", "coronal.png"),
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


if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    color_map_tool = ColorMapTool()
    layout_dicom_tool = LayoutDicomTool()

    viewer_toolbar = VolumeViewerToolbar(
        path_icones="",
        color_map_tool=color_map_tool,
        layout_tool=layout_dicom_tool,
    )

    viewer_toolbar.show()
    sys.exit(app.exec())