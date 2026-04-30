import os
from PySide6 import QtWidgets, QtCore, QtGui
from core.components.windows.base.janelas import JanelaBase
from core.components.windows.window_2d.context_menu_2d import ContextMenu2D

class Janela2D(JanelaBase):
    sliceChanged = QtCore.Signal(int)
    maximizeRequested = QtCore.Signal(bool)
    lutChanged = QtCore.Signal(str)

    def __init__(self, titulo: str, cor: str, parent=None):
        super().__init__(titulo, cor, parent)
        self.is_maximized = False
        self.vtk_property = None
        self._setup_specific_ui()
        self._setup_interactions()
        self.vtkWidget.installEventFilter(self)

    def eventFilter(self, source, event):
        if source is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() == QtCore.Qt.LeftButton:
                self._toggle_maximize()
                return True
        return super().eventFilter(source, event)

    def _setup_specific_ui(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.path_icons = os.path.abspath(os.path.join(base_dir, "", "..", "..", "icons"))

        self.combo_proj = QtWidgets.QComboBox()
        self.combo_proj.addItems(["Axial", "Coronal", "Sagittal"])
        self.combo_proj.setFixedWidth(85)
        self.combo_proj.setCurrentText(self.titulo)

        self.slider_corte = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_corte.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.slider_corte.setStyleSheet("""
            QSlider::handle:horizontal {
                background: #3EA6FA;
                width: 6px;
                border-radius: 3px;
            }
        """)

        self.lbl_mm = QtWidgets.QLabel("0.0 mm")
        self.lbl_mm.setFixedWidth(65)
        self.lbl_mm.setAlignment(QtCore.Qt.AlignCenter)

        self.btn_maximize = QtWidgets.QPushButton()
        self.btn_maximize.setFixedSize(24, 24)
        self.btn_maximize.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_maximize.clicked.connect(self._toggle_maximize)
        self._update_maximize_icon()

        self.adicionar_controle(self.combo_proj)
        self.adicionar_controle(QtWidgets.QLabel(" Slice:"))
        self.adicionar_controle(self.slider_corte)
        self.adicionar_controle(self.lbl_mm)
        self.adicionar_controle(self.btn_maximize)

        self.slider_corte.valueChanged.connect(self.sliceChanged.emit)

        self.vtkWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.vtkWidget.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        menu = ContextMenu2D(self)
        menu.exec_(self.vtkWidget.mapToGlobal(pos))

    def _update_maximize_icon(self):
        icon_name = "minimizar.png" if self.is_maximized else "maximizar.png"
        icon_path = os.path.join(self.path_icons, icon_name)
        if os.path.exists(icon_path):
            self.btn_maximize.setIcon(QtGui.QIcon(icon_path))
            self.btn_maximize.setIconSize(QtCore.QSize(16, 16))

        self.btn_maximize.setStyleSheet("""
            QPushButton { border: none; background: transparent; } 
            QPushButton:hover { background: #444; border-radius: 3px; }
        """)

    def _toggle_maximize(self):
        self.is_maximized = not self.is_maximized
        self._update_maximize_icon()
        self.maximizeRequested.emit(self.is_maximized)

    def _setup_interactions(self):
        if hasattr(self.vtkWidget, "AddObserver"):
            self.vtkWidget.AddObserver("MouseWheelForwardEvent", self._handle_wheel)
            self.vtkWidget.AddObserver("MouseWheelBackwardEvent", self._handle_wheel)

    def _handle_wheel(self, obj, event):
        step = 1 if event == "MouseWheelForwardEvent" else -1
        self.slider_corte.setValue(self.slider_corte.value() + step)

    def apply_lut(self, lut_name: str):
        self.lutChanged.emit(lut_name)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._toggle_maximize()
        super().mouseDoubleClickEvent(event)