import os
from PySide6 import QtWidgets, QtCore, QtGui
from core.components.bases.base_central_area import CentralAreaBase
from core.components.central_area.window_2d_.context_menu_2d import ContextMenu2D


class Viewer2D_Widget_CentralArea(CentralAreaBase):
    sliceChanged = QtCore.Signal(int)
    maximizeRequested = QtCore.Signal(bool)
    lutChanged = QtCore.Signal(str)

    def __init__(self, context, title: str, cor: str, parent=None):
        super().__init__(context=context, title=title, cor_identificacao=cor, parent=parent)

        self.is_maximized = False
        self.vtk_property = None

        self._setup_specific_ui()
        self._setup_interactions()
        self._connect_events()

        if self.vtkWidget:
            self.vtkWidget.installEventFilter(self)

    def _connect_events(self):
        """Conecta os eventos globais do sistema de cenas e volumes ao visualizador 2D."""
        if self.context and hasattr(self.context, "event_bus") and self.context.event_bus:
            event_bus = self.context.event_bus

            # Exemplo de escuta para quando um DICOM for carregado
            if hasattr(event_bus, "subscribe"):
                event_bus.subscribe("DICOM_LOADED", self._on_dicom_loaded)
                event_bus.subscribe("LUT_CHANGED", self._on_lut_event_received)
            elif hasattr(event_bus, "connect"):  # Dependendo se usa Signal do Qt ou PubSub customizado
                pass

    def _on_dicom_loaded(self, *args, **kwargs):
        # Captura tanto argumentos posicionais quanto nomeados (como 'volume', 'path', etc.)
        volume = kwargs.get("volume") or (args[0] if args else None)


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
        self.combo_proj.setCurrentText(self.title)

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

        self.add_control(self.combo_proj)
        self.add_control(QtWidgets.QLabel(" Slice:"))
        self.add_control(self.slider_corte)
        self.add_control(self.lbl_mm)
        self.add_control(self.btn_maximize)

        self.slider_corte.valueChanged.connect(self.sliceChanged.emit)

        self.vtkWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.vtkWidget.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        menu = ContextMenu2D(parent=self, context=self.context, scene_manager=self.scene_manager)
        menu.exec(self.vtkWidget.mapToGlobal(pos))

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
        pass

    def wheelEvent(self, event: QtGui.QWheelEvent):
        """Trata o evento de rolagem diretamente no nível do Widget Qt para evitar conflito com o zoom do VTK."""
        angle = event.angleDelta().y()
        if angle != 0:
            step = 1 if angle > 0 else -1
            novo_valor = self.slider_corte.value() + step
            self.slider_corte.setValue(novo_valor)
            event.accept()
        else:
            super().wheelEvent(event)

    def apply_lut(self, lut_name: str):
        self.lutChanged.emit(lut_name)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._toggle_maximize()
        super().mouseDoubleClickEvent(event)

    def _on_lut_event_received(self, lut_name: str = None, **kwargs):
        """Captura o evento global de mudança de LUT emitido pelo ColorMapTool."""
        name = lut_name or kwargs.get("lut_name")
        if name:
            self.apply_lut(name)