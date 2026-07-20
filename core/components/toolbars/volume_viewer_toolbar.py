import os
from PySide6 import QtWidgets, QtCore, QtGui
from core.volume.lookup_table.lut_presets import LUTPresets
from core.components.bases.base_toolbar import BaseToolbar, AppContext
from core.components.tools.color_map_tool import ColorMapTool
from core.components.tools.layout_dicom_tool import LayoutDicomTool
from core.localization.translator import get_base_dir  # Import necessário para localizar os ícones


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


class VolumeViewerToolbar(BaseToolbar):
    def __init__(self, app_context: AppContext, parent=None):
        # Inicializa com o contexto centralizado
        super().__init__("Volume Viewer", app_context, parent, is_movable=False)
        self._combo_layout = None
        self._combo_lut = None

    def get_icon(self, icon_name: str, fallback=QtWidgets.QStyle.StandardPixmap.SP_FileIcon) -> QtGui.QIcon:
        """Método helper da classe para carregar ícones com segurança."""
        path = get_base_dir() / "appearance" / "icons" / icon_name
        if path.exists():
            return QtGui.QIcon(str(path))
        return QtWidgets.QApplication.style().standardIcon(fallback)

    def setup_ui(self) -> None:
        """Configuração da UI utilizando a estrutura da BaseToolbar."""
        self.setFixedHeight(38)
        self.layout().setSpacing(12)
        self.layout().setContentsMargins(10, 0, 10, 0)

        # 1. Layout Control (Custom widget)
        self.addWidget(QtWidgets.QLabel("Layout"))
        self._combo_layout = QtWidgets.QComboBox()
        self._combo_layout.setFixedWidth(130)
        self._populate_layouts()
        self._combo_layout.currentTextChanged.connect(self._on_layout_changed)
        self.addWidget(self._combo_layout)

        self.add_separator()

        # 2. Color Map Control (Custom widget)
        self.addWidget(QtWidgets.QLabel("Color Map"))
        self._combo_lut = QtWidgets.QComboBox()
        self._combo_lut.setFixedWidth(130)
        self._combo_lut.setItemDelegate(LUTDelegate(self._combo_lut))
        self._combo_lut.addItems(list(LUTPresets.PRESETS.keys()))
        self._combo_lut.currentTextChanged.connect(self._on_lut_changed)
        self.addWidget(self._combo_lut)

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
            icon = self.get_icon(img)
            self._combo_layout.addItem(icon, nome)

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
            self._combo_lut.setCurrentText(lut_name)
            self._combo_lut.blockSignals(False)

    def set_layout_text(self, layout_name: str):
        if self._combo_layout:
            self._combo_layout.blockSignals(True)
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
    viewer_toolbar.initialize()
    viewer_toolbar.show()
    sys.exit(app.exec())