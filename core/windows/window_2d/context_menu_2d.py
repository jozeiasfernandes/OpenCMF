from PySide6 import QtWidgets, QtGui, QtCore


class ContextMenu2D(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_menu()

    def _build_menu(self):
        self.setStyleSheet("""
            QMenu { background-color: #2D2D2D; color: white; border: 1px solid #555; }
            QMenu::item:selected { background-color: #3EA6FA; }
            QMenu::separator { background-color: #555; height: 1px; margin: 4px; }
        """)

        self.menu_mouse = self.addMenu("Mouse")
        self.act_scroll = self.menu_mouse.addAction("Scroll slices")
        self.act_wl = self.menu_mouse.addAction("Brightness/Contrast")
        self.act_zoom = self.menu_mouse.addAction("Zoom")

        self.menu_views = self.addMenu("Views")
        self.act_axial = self.menu_views.addAction("Axial")
        self.act_coronal = self.menu_views.addAction("Coronal")
        self.act_sagital = self.menu_views.addAction("Sagittal")
        self.act_3d = self.menu_views.addAction("3D")
        self.menu_views.addSeparator()
        self.act_panoramic = self.menu_views.addAction("Panoramic curve")
        self.act_data = self.menu_views.addAction("CT Data")

        self.act_lut = self.addAction("LUT")

        self.menu_display = self.addMenu("Display")
        self.act_vol = self.menu_display.addAction("Volume")
        self.act_obj = self.menu_display.addAction("Objects")
        self.act_ann = self.menu_display.addAction("Annotations")

        for act in [self.act_vol, self.act_obj, self.act_ann]:
            act.setCheckable(True)
            act.setChecked(True)

        self.addSeparator()

        self.act_ruler = self.addAction("Ruler")
        self.act_print = self.addAction("Print")
        self.act_fullscreen = self.addAction("Full screen")