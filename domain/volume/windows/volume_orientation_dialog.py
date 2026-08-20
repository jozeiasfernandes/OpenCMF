from __future__ import annotations
from typing import Optional, Dict, Any, Tuple
from PySide6 import QtWidgets, QtCore, QtGui

import vtk
from vtkmodules.all import vtkRenderer

try:
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
except ImportError:
    try:
        from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    except ImportError:
        QVTKRenderWindowInteractor = None
        print("Aviso: QVTKRenderWindowInteractor não pôde ser importado. Verifique a instalação do VTK.")

from typing import Optional, Dict, Any, Tuple
from PySide6 import QtWidgets, QtCore, QtGui

# Settings
from core.settings.localization.translator import tr


class VolumeOrientationWindow(QtWidgets.QDialog):
    """Janela de verificação, orientação e alinhamento prévio do volume DICOM."""

    def __init__(self, volume_data: Optional[Any] = None, dimensions: Optional[Tuple[int, int, int]] = None,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.volume_data = volume_data

        # Define dimensões dinâmicas (padrão 500 caso não venha nada)
        self.dims = dimensions or (500, 500, 500)

        self.rotation_angles: Tuple[float, float, float] = (0.0, 0.0, 0.0)

        self.setWindowTitle(tr("import.volume.orientation", "Orientação e Alinhamento do Volume"))
        self.resize(600, 400)

        self._init_ui()

    def _init_ui(self):
        """Inicializa os componentes visuais da interface (Grid 2x2 simulando o layout de referência)."""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Grid Superior/Central: 4 quadrantes (3 visualizadores ortogonais + 1 painel de controle)
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(5)

        # 1. Vista XY (Axial)
        self.view_xy_container = self._create_viewport_container("Vista XY")
        grid_layout.addWidget(self.view_xy_container, 0, 0)

        # 2. Vista XZ (Coronal)
        self.view_xz_container = self._create_viewport_container("Vista XZ")
        grid_layout.addWidget(self.view_xz_container, 0, 1)

        # 3. Vista YZ (Sagital)
        self.view_yz_container = self._create_viewport_container("Vista YZ")
        grid_layout.addWidget(self.view_yz_container, 1, 0)

        # 4. Painel de Opções, Alinhamento e ROI (Inferior Direito)
        self.control_panel = self._create_control_panel()
        grid_layout.addWidget(self.control_panel, 1, 1)

        main_layout.addLayout(grid_layout, stretch=1)

        # Barra de Botões Inferior (Confirmar / Cancelar)
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.addStretch()

        self.btn_cancel = QtWidgets.QPushButton(tr("commons.close_button", "Cancelar"))
        self.btn_cancel.clicked.connect(self.reject)
        footer_layout.addWidget(self.btn_cancel)

        self.btn_confirm = QtWidgets.QPushButton(tr("commons.confirm", "Confirmar Orientação"))
        self.btn_confirm.setObjectName("okButton")
        self.btn_confirm.setDefault(True)
        self.btn_confirm.clicked.connect(self.accept)
        footer_layout.addWidget(self.btn_confirm)

        main_layout.addLayout(footer_layout)

    def _create_viewport_container(self, title: str) -> QtWidgets.QGroupBox:
        """Cria um container contendo um renderizador VTK real para as vistas ortogonais."""
        group = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QVBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)

        # Widget interativo do VTK substituindo o QLabel estático
        vtk_widget = QVTKRenderWindowInteractor(group)
        vtk_widget.setMinimumHeight(180)

        # Configuração básica do pipeline VTK para o slice
        renderer = vtkRenderer()
        renderer.SetBackground(0.0, 0.0, 0.0)  # Fundo preto
        vtk_widget.GetRenderWindow().AddRenderer(renderer)

        # Armazena referências para posterior manipulação dos cortes se necessário
        if not hasattr(self, "_vtk_viewports"):
            self._vtk_viewports = {}
        self._vtk_viewports[title] = {
            "widget": vtk_widget,
            "renderer": renderer
        }

        layout.addWidget(vtk_widget)
        return group

    def _create_control_panel(self) -> QtWidgets.QScrollArea:
        """Cria o painel lateral direito contendo as opções de imagiologia, alinhamento e volume pretendido."""
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(15)

        # --- Seção: Opções / Modo Imagiologia ---
        group_options = QtWidgets.QGroupBox("Opções")
        layout_opts = QtWidgets.QFormLayout(group_options)

        self.combo_imaging_mode = QtWidgets.QComboBox()
        self.combo_imaging_mode.addItems(["MIP", "MinIP", "Average", "Alpha"])
        layout_opts.addRow("Modo Imagiologia", self.combo_imaging_mode)
        layout.addWidget(group_options)

        # --- Seção: Alinhamento e Rotações ---
        group_alignment = QtWidgets.QGroupBox("Alinhamento")
        layout_align = QtWidgets.QVBoxLayout(group_alignment)

        self.spin_angle_x = self._create_angle_spinbox("Ângulo X", layout_align, self._on_angle_x_changed)
        self.spin_angle_y = self._create_angle_spinbox("Ângulo Y", layout_align, self._on_angle_y_changed)
        self.spin_angle_z = self._create_angle_spinbox("Ângulo Z", layout_align, self._on_angle_z_changed)

        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_undo = QtWidgets.QPushButton("Anular")
        self.btn_undo.clicked.connect(self.reset_rotations)
        btn_layout.addWidget(self.btn_undo)

        self.btn_reset_rotation = QtWidgets.QPushButton("Repor Rotação")
        self.btn_reset_rotation.clicked.connect(self.reset_rotations)
        btn_layout.addWidget(self.btn_reset_rotation)

        layout_align.addLayout(btn_layout)
        layout.addWidget(group_alignment)

        # --- Seção: Volume Pretendido (ROI) ---
        group_roi = QtWidgets.QGroupBox("Volume Pretendido")
        layout_roi = QtWidgets.QFormLayout(group_roi)

        # 🚀 Usa as dimensões reais repassadas na inicialização (X, Y, Z)
        dx, dy, dz = self.dims
        self.spin_min_x, self.spin_max_x = self._create_min_max_spinbox("Eixo X", 0, dx, layout_roi)
        self.spin_min_y, self.spin_max_y = self._create_min_max_spinbox("Eixo Y", 0, dy, layout_roi)
        self.spin_min_z, self.spin_max_z = self._create_min_max_spinbox("Eixo Z", 0, dz, layout_roi)

        # Define os valores máximos iniciais como o topo do intervalo
        self.spin_max_x.setValue(dx)
        self.spin_max_y.setValue(dy)
        self.spin_max_z.setValue(dz)

        layout.addWidget(group_roi)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def _create_angle_spinbox(self, label_text: str, parent_layout: QtWidgets.QVBoxLayout,
                              callback) -> QtWidgets.QDoubleSpinBox:
        """Método auxiliar para criar controles de rotação estéticos."""
        h_layout = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(label_text)
        spin = QtWidgets.QDoubleSpinBox()
        spin.setRange(-180.0, 180.0)
        spin.setSingleStep(1.0)
        spin.setValue(0.0)
        spin.setSuffix("°")
        spin.valueChanged.connect(callback)

        h_layout.addWidget(lbl)
        h_layout.addWidget(spin)
        parent_layout.addLayout(h_layout)
        return spin

    def _create_min_max_spinbox(self, axis_label: str, min_val: int, max_val: int,
                                form_layout: QtWidgets.QFormLayout):
        """Cria campos duplos para controle de limites do volume (ROI)."""
        layout = QtWidgets.QHBoxLayout()
        spin_min = QtWidgets.QSpinBox()
        spin_min.setRange(min_val, max_val)
        spin_min.setValue(min_val)

        spin_max = QtWidgets.QSpinBox()
        spin_max.setRange(min_val, max_val)
        spin_max.setValue(max_val)

        layout.addWidget(QtWidgets.QLabel("Mín:"))
        layout.addWidget(spin_min)
        layout.addWidget(QtWidgets.QLabel("Máx:"))
        layout.addWidget(spin_max)

        form_layout.addRow(f"{axis_label} Bounds", layout)
        return spin_min, spin_max

    def _on_angle_x_changed(self, value: float):
        """Atualiza o estado do eixo X."""
        self.rotation_angles = (value, self.rotation_angles[1], self.rotation_angles[2])

    def _on_angle_y_changed(self, value: float):
        """Atualiza o estado do eixo Y."""
        self.rotation_angles = (self.rotation_angles[0], value, self.rotation_angles[2])

    def _on_angle_z_changed(self, value: float):
        """Atualiza o estado do eixo Z."""
        self.rotation_angles = (self.rotation_angles[0], self.rotation_angles[1], value)

    def reset_rotations(self):
        """Reseta todos os ângulos de rotação para zero."""
        self.spin_angle_x.setValue(0.0)
        self.spin_angle_y.setValue(0.0)
        self.spin_angle_z.setValue(0.0)
        self.rotation_angles = (0.0, 0.0, 0.0)

    def get_orientation_parameters(self) -> Dict[str, Any]:
        """Retorna os parâmetros finais de orientação, rotação e ROI configurados pelo usuário."""
        return {
            "imaging_mode": self.combo_imaging_mode.currentText(),
            "rotation_angles": self.rotation_angles,
            "roi_bounds": {
                "x": (self.spin_min_x.value(), self.spin_max_x.value()),
                "y": (self.spin_min_y.value(), self.spin_max_y.value()),
                "z": (self.spin_min_z.value(), self.spin_max_z.value())
            }
        }


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = VolumeOrientationWindow()

    if window.exec() == QtWidgets.QDialog.Accepted:
        params = window.get_orientation_parameters()
        print("Parâmetros de Orientação Confirmados:", params)
    else:
        print("Orientação cancelada pelo usuário.")

    sys.exit(0)