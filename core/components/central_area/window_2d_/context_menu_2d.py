from PySide6 import QtWidgets
from domain.volume.visualization.lut.lut_presets import LUTPresets

MENU_STYLE = """
    QMenu { 
        background-colors: #2D2D2D; 
        colors: white; 
        border: 1px solid #555; 
    }
    QMenu#LUT_SUBMENU {
        min-width: 200px;
    }
    QMenu::item { 
        padding: 2px 1px;
        min-height: 26px;
        background: transparent;
    }
    QMenu::item:selected { 
        background-colors: #3EA6FA; 
    }
    QMenu#LUT_SUBMENU::icon {
        position: absolute;
        top: 1px;
        left: 1px;
        bottom: 1px;
        right: 1px;
        width: 190px;
        height: 22px;
        padding: 0px;
        margin: 0px;
    }
    QMenu#LUT_SUBMENU::item {
        padding-left: 1px;
    }
"""


class ContextMenu2D(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(MENU_STYLE)
        self._build_menu()

    def _build_menu(self):
        self._setup_mouse_menu()
        self._setup_views_menu()
        self._setup_lut_menu()
        self._setup_display_menu()

        self.addSeparator()

        self.act_ruler = self.addAction("Ruler")
        self.act_print = self.addAction("Print")
        self.act_fullscreen = self.addAction("Full screen")

    def _setup_mouse_menu(self):
        self.menu_mouse = self.addMenu("Mouse")
        self.act_scroll = self.menu_mouse.addAction("Scroll slices")
        self.act_wl = self.menu_mouse.addAction("Brightness/Contrast")
        self.act_zoom = self.menu_mouse.addAction("Zoom")

    def _setup_views_menu(self):
        self.menu_views = self.addMenu("Views")
        self.act_axial = self.menu_views.addAction("Axial")
        self.act_coronal = self.menu_views.addAction("Coronal")
        self.act_sagital = self.menu_views.addAction("Sagittal")
        self.act_3d = self.menu_views.addAction("3D")

        self.menu_views.addSeparator()

        self.act_panoramic = self.menu_views.addAction("Panoramic curve")
        self.act_data = self.menu_views.addAction("CT Data")

    def _setup_lut_menu(self):
        self.menu_lut = self.addMenu("Color Map")
        self.menu_lut.setObjectName("LUT_SUBMENU")
        self.menu_lut.setMinimumWidth(200)

        for name in LUTPresets.PRESETS.keys():
            # Criamos uma ação de widget para controle total do layout
            action_widget = QtWidgets.QWidgetAction(self.menu_lut)

            # Criamos o container (Label) que exibirá o degradê
            label = QtWidgets.QLabel()
            pixmap = LUTPresets.get_lut_icon(name, width=190, height=22).pixmap(190, 22)
            label.setPixmap(pixmap)
            label.setContentsMargins(5, 2, 5, 2)
            label.setToolTip(name)

            # Estilo para o item reagir ao mouse (hover) como um menu normal
            label.setStyleSheet("""
                QLabel { padding: 1px; background: transparent; }
                QLabel:hover { background-colors: #3EA6FA; }
            """)

            # Definimos o widget na ação
            action_widget.setDefaultWidget(label)

            # Conectamos o clique do label à função de aplicação do LUT
            # Usamos o evento de clique do mouse no widget
            label.mouseReleaseEvent = lambda event, n=name: [
                self.parent().apply_lut(n),
                self.menu_lut.close(),
                self.close()
            ]

            self.menu_lut.addAction(action_widget)

    def _setup_display_menu(self):
        self.menu_display = self.addMenu("Display")
        self.act_vol = self.menu_display.addAction("Volume")
        self.act_obj = self.menu_display.addAction("Objects")
        self.act_ann = self.menu_display.addAction("Annotations")

        for act in [self.act_vol, self.act_obj, self.act_ann]:
            act.setCheckable(True)
            act.setChecked(True)