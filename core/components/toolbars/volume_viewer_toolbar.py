from PySide6 import QtWidgets, QtCore, QtGui

from domain.volume.visualization.lut.lut_presets import LUTPresets

from core.components.bases.base_toolbar.base_toolbar import BaseToolbar, AppContext

# Settings
from core.settings.icons.icons_manager import IconManager
from core.settings.localization.translator import tr


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
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawText(rect, QtCore.Qt.AlignCenter, name)
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(100, 28)


class VolumeViewerToolbar(BaseToolbar):
    def __init__(self, app_context: AppContext, parent=None):
        super().__init__(tr("volume_viewer.title", "Volume Viewer"), app_context, parent, is_movable=False)
        self._combo_layout = None
        self._combo_lut = None

    def get_icon(self, icon_name: str, fallback=QtWidgets.QStyle.StandardPixmap.SP_FileIcon) -> QtGui.QIcon:
        """Método helper utilizando o IconManager centralizado."""
        icon_manager = IconManager.get_instance()
        icon = icon_manager.get_icon(icon_name)
        if not icon.isNull():
            return icon
        return QtWidgets.QApplication.style().standardIcon(fallback)

    def setup_ui(self) -> None:
        """Configuração da UI utilizando a estrutura da BaseToolbar."""
        self.setFixedHeight(38)
        self.layout().setSpacing(12)
        self.layout().setContentsMargins(10, 0, 10, 0)

        # 1. Layout Control (Custom widget)
        self.addWidget(QtWidgets.QLabel(tr("volume_viewer.layout", "Layout")))
        self._combo_layout = QtWidgets.QComboBox()
        self._combo_layout.setFixedWidth(130)
        self._populate_layouts()
        self._combo_layout.currentIndexChanged.connect(self._on_layout_combo_changed)
        self.addWidget(self._combo_layout)

        self.add_separator()

        # 2. Color Map Control (Custom widget)
        self.addWidget(QtWidgets.QLabel(tr("volume_viewer.color_map", "Color Map")))
        self._combo_lut = QtWidgets.QComboBox()
        self._combo_lut.setFixedWidth(130)
        self._combo_lut.setItemDelegate(LUTDelegate(self._combo_lut))
        self._populate_luts()
        self._combo_lut.currentIndexChanged.connect(self._on_lut_combo_changed)
        self.addWidget(self._combo_lut)

    def _populate_layouts(self):
        opcoes = [
            (tr("volume_viewer.layout.quadrants", "4 Quadrantes"), "4_viewer", "4 Quadrantes"),
            (tr("volume_viewer.layout.3d_highlight", "3D Destacado"), "3_1_viewer", "3D Destacado"),
            (tr("volume_viewer.layout.only_3d", "Apenas 3D"), "1_3d_viewer", "Apenas 3D"),
            (tr("volume_viewer.layout.axial", "Axial"), "axial", "Axial"),
            (tr("volume_viewer.layout.sagittal", "Sagital"), "sagital", "Sagital"),
            (tr("volume_viewer.layout.coronal", "Coronal"), "coronal", "Coronal"),
        ]
        for label, img, data_key in opcoes:
            icon = self.get_icon(img)
            self._combo_layout.addItem(icon, label, data_key)

    def _populate_luts(self):
        for name in list(LUTPresets.PRESETS.keys()):
            self._combo_lut.addItem(name, name)

    def _on_layout_combo_changed(self, index: int):
        data_key = self._combo_layout.itemData(index)
        if data_key:
            self._on_layout_changed(data_key)

    def _on_lut_combo_changed(self, index: int):
        data_key = self._combo_lut.itemData(index)
        if data_key:
            self._on_lut_changed(data_key)

    def _on_layout_changed(self, name: str):
        layout_tool = self.tool_manager.get_tool("layout_dicom_tool")
        if layout_tool and hasattr(layout_tool, 'apply_layout'):
            layout_tool.apply_layout(name)

    def _on_lut_changed(self, name: str):
        color_map_tool = self.tool_manager.get_tool("color_map_tool")
        if color_map_tool and hasattr(color_map_tool, 'apply_lut'):
            color_map_tool.apply_lut(name)

    def set_lut_text(self, lut_name: str):
        if self._combo_lut:
            self._combo_lut.blockSignals(True)
            index = self._combo_lut.findData(lut_name)
            if index >= 0:
                self._combo_lut.setCurrentIndex(index)
            else:
                self._combo_lut.setCurrentText(lut_name)
            self._combo_lut.blockSignals(False)

    def set_layout_text(self, layout_name: str):
        if self._combo_layout:
            self._combo_layout.blockSignals(True)
            index = self._combo_layout.findData(layout_name)
            if index >= 0:
                self._combo_layout.setCurrentIndex(index)
            else:
                self._combo_layout.setCurrentText(layout_name)
            self._combo_layout.blockSignals(False)


if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets


    class MockToolManager:
        def get_tool(self, name): return None


    class MockSceneManager: pass


    class MockSettings:
        def get(self, key, default=None): return default
        def set(self, key, value): pass


    app = QtWidgets.QApplication(sys.argv)

    app_context = AppContext(
        tool_manager=MockToolManager(),
        scene_manager=MockSceneManager(),
        settings=MockSettings()
    )

    viewer_toolbar = VolumeViewerToolbar(app_context=app_context)
    viewer_toolbar.show()
    sys.exit(app.exec())