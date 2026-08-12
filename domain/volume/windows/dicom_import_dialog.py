from __future__ import annotations
from typing import Optional, Dict, Any, List, Tuple
from PySide6 import QtWidgets, QtCore, QtGui

# Settings
from core.settings.localization.translator import tr

# Thumbnail
from domain.volume.visualization.volume_viewer.thumbnail_generator.thumbnail_generator import DicomThumbnailGenerator


class DicomImportWindow(QtWidgets.QDialog):
    """Janela de seleção, pré-visualização e importação de séries DICOM."""

    def __init__(self, series_list: Optional[List[Dict[str, Any]]] = None, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.series_list = series_list or []
        self.selected_series_index: int = -1

        self.setWindowTitle(tr("import.volumes.dicom", "Importar DICOM / Tomografia"))
        self.resize(620, 480)

        self._init_ui()
        if self.series_list:
            self._populate_table()

    def _init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. Tabela Superior de Seleção de Séries
        self.table_series = QtWidgets.QTableWidget()
        self.table_series.setColumnCount(6)
        self.table_series.setHorizontalHeaderLabels([
            "Series #", "Series description", "Modality", "Size", "Count", "Date added"
        ])
        self.table_series.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_series.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_series.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_series.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_series.setFixedHeight(150)
        self.table_series.itemSelectionChanged.connect(self._on_series_selection_changed)
        main_layout.addWidget(self.table_series)

        # 2. Painel Principal de Pré-visualização
        preview_container = QtWidgets.QWidget()
        preview_layout = QtWidgets.QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(5, 5, 5, 5)
        preview_layout.setSpacing(6)

        self.lbl_patient_info = QtWidgets.QLabel("NENHUM PACIENTE SELECIONADO - 00000")
        self.lbl_patient_info.setStyleSheet("font-weight: bold; font-size: 13px;")
        preview_layout.addWidget(self.lbl_patient_info)

        self.lbl_series_date = QtWidgets.QLabel("---")
        preview_layout.addWidget(self.lbl_series_date)

        # Bloco estilizado com fundo azul idêntico à referência
        self.card_widget = QtWidgets.QWidget()
        self.card_widget.setStyleSheet("""
            QWidget {
                background-color: #2b82c9;
                border-radius: 4px;
                color: white;
            }
        """)
        card_layout = QtWidgets.QHBoxLayout(self.card_widget)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(10)

        # Miniatura
        self.lbl_thumbnail = QtWidgets.QLabel()
        self.lbl_thumbnail.setFixedSize(140, 140)
        self.lbl_thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_thumbnail.setText("Sem Pré-via")
        self.lbl_thumbnail.setStyleSheet("background-color: #1a1a1a; border-radius: 2px; color: #888888;")
        card_layout.addWidget(self.lbl_thumbnail)

        # Descrição central dentro do card azul
        self.lbl_series_desc = QtWidgets.QLabel("Selecione uma série acima...")
        self.lbl_series_desc.setWordWrap(True)
        self.lbl_series_desc.setStyleSheet("background: transparent; color: white;")
        card_layout.addWidget(self.lbl_series_desc, stretch=1)

        # Informações de voxels à direita dentro do card azul
        self.lbl_voxel_info = QtWidgets.QLabel("--- x --- x --- voxels\n0.00 x 0.00 x 0.00 mm\n---")
        self.lbl_voxel_info.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_voxel_info.setStyleSheet("background: transparent; color: white; font-weight: bold;")
        card_layout.addWidget(self.lbl_voxel_info, stretch=1)

        preview_layout.addWidget(self.card_widget)
        main_layout.addWidget(preview_container)

        # 3. Controles Inferiores: Fatores de amostragem + Botões OK/Cancel
        bottom_layout = QtWidgets.QHBoxLayout()

        sampling_layout = QtWidgets.QHBoxLayout()
        sampling_layout.addWidget(QtWidgets.QLabel("Fatores de amostragem"))

        sampling_layout.addWidget(QtWidgets.QLabel("X"))
        self.spin_x = QtWidgets.QDoubleSpinBox()
        self.spin_x.setRange(0.1, 10.0)
        self.spin_x.setSingleStep(0.1)
        self.spin_x.setValue(1.0)
        sampling_layout.addWidget(self.spin_x)

        sampling_layout.addWidget(QtWidgets.QLabel("Y"))
        self.spin_y = QtWidgets.QDoubleSpinBox()
        self.spin_y.setRange(0.1, 10.0)
        self.spin_y.setSingleStep(0.1)
        self.spin_y.setValue(1.0)
        sampling_layout.addWidget(self.spin_y)

        sampling_layout.addWidget(QtWidgets.QLabel("Z"))
        self.spin_z = QtWidgets.QDoubleSpinBox()
        self.spin_z.setRange(0.1, 10.0)
        self.spin_z.setSingleStep(0.1)
        self.spin_z.setValue(1.0)
        sampling_layout.addWidget(self.spin_z)

        bottom_layout.addLayout(sampling_layout)
        bottom_layout.addStretch()

        self.btn_ok = QtWidgets.QPushButton("OK")
        self.btn_ok.setObjectName("okButton")
        self.btn_ok.clicked.connect(self.accept)
        bottom_layout.addWidget(self.btn_ok)

        self.btn_cancel = QtWidgets.QPushButton(tr("common.close_button", "Fechar"))
        self.btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(bottom_layout)

    def _populate_table(self):
        self.table_series.setRowCount(len(self.series_list))
        for row, series in enumerate(self.series_list):
            self.table_series.setItem(row, 0, QtWidgets.QTableWidgetItem(str(series.get("number", ""))))
            self.table_series.setItem(row, 1, QtWidgets.QTableWidgetItem(str(series.get("description", ""))))
            self.table_series.setItem(row, 2, QtWidgets.QTableWidgetItem(str(series.get("modality", "CT"))))

            size_str = f"{series.get('width', 512)}x{series.get('height', 512)}"
            self.table_series.setItem(row, 3, QtWidgets.QTableWidgetItem(size_str))

            self.table_series.setItem(row, 4, QtWidgets.QTableWidgetItem(str(series.get("count", 1))))
            self.table_series.setItem(row, 5, QtWidgets.QTableWidgetItem(str(series.get("date", ""))))

        if self.series_list:
            self.table_series.selectRow(0)
            self.selected_series_index = 0
            self._on_series_selection_changed()

    def _on_series_selection_changed(self):
        selected_rows = self.table_series.selectionModel().selectedRows()
        if not selected_rows:
            self.selected_series_index = -1
            self.lbl_thumbnail.clear()
            self.lbl_thumbnail.setText("Sem Pré-via")
            return

        self.selected_series_index = selected_rows[0].row()
        if 0 <= self.selected_series_index < len(self.series_list):
            series = self.series_list[self.selected_series_index]

            patient_name = series.get("patient_name", "PACIENTE DESCONHECIDO")
            patient_id = series.get("patient_id", "00000")
            self.lbl_patient_info.setText(f"{patient_name} - {patient_id}")

            date_str = series.get("date", "---")
            uid_str = series.get("uid", "---")
            self.lbl_series_date.setText(f"{date_str} - {uid_str}")

            desc = series.get("description", "")
            mod = series.get("modality", "CT")
            self.lbl_series_desc.setText(f"{date_str}\n{mod},\n{desc}")

            w = series.get("width", 600)
            h = series.get("height", 600)
            c = series.get("count", 399)
            sx = series.get("spacing_x", 0.15)
            sy = series.get("spacing_y", 0.15)
            sz = series.get("spacing_z", 0.15)
            tag = series.get("tag", "ORIGINAL")

            self.lbl_voxel_info.setText(f"{w} x {h} x {c} voxels\n{sx:.2f} x {sy:.2f} x {sz:.2f} mm\n{tag}")

            # Tenta carregar o vtk_image se disponível no dicionário da série
            vtk_image = series.get("vtk_image", None)
            if vtk_image:
                pixmap = DicomThumbnailGenerator.generate_thumbnail(vtk_image, target_size=140)
                if not pixmap.isNull():
                    self.lbl_thumbnail.setPixmap(pixmap)
                else:
                    self.lbl_thumbnail.clear()
                    self.lbl_thumbnail.setText("Erro na Pré-via")
            else:
                self.lbl_thumbnail.clear()
                self.lbl_thumbnail.setText("Sem Imagem VTK")

    def get_selected_series(self) -> Optional[Dict[str, Any]]:
        """Retorna os dados da série atualmente selecionada na tabela."""
        if 0 <= self.selected_series_index < len(self.series_list):
            return self.series_list[self.selected_series_index]
        return None

    def get_sampling_factors(self) -> Tuple[float, float, float]:
        """Retorna os fatores de amostragem configurados (X, Y, Z)."""
        return (self.spin_x.value(), self.spin_y.value(), self.spin_z.value())

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    mock_series = [
        {
            "number": 10100,
            "description": "TOPOGRAMA",
            "modality": "CT",
            "width": 512,
            "height": 297,
            "count": 3,
            "date": "2026-04-05 15:128",
            "patient_name": "KAWABE THIAGO HITOSHI MEIRELES",
            "patient_id": "93251",
            "uid": "1.2.826.0.1.3680043.9.1938.133704564476357338714818046",
            "spacing_x": 0.5,
            "spacing_y": 0.5,
            "spacing_z": 1.0,
            "tag": "LOCALIZER"
        },
        {
            "number": 10302,
            "description": "SEIOS DA FACE",
            "modality": "CT",
            "width": 600,
            "height": 600,
            "count": 399,
            "date": "2012-11-01 15:329",
            "patient_name": "KAWABE THIAGO HITOSHI MEIRELES",
            "patient_id": "93251",
            "uid": "1.2.826.0.1.3680043.9.1938.133704564476357338714818046",
            "spacing_x": 0.15,
            "spacing_y": 0.15,
            "spacing_z": 0.15,
            "tag": "ORIGINAL"
        }
    ]

    window = DicomImportWindow(series_list=mock_series)

    if window.exec() == QtWidgets.QDialog.Accepted:
        selected = window.get_selected_series()
        factors = window.get_sampling_factors()
        print("Série selecionada:", selected)
        print("Fatores de amostragem:", factors)
    else:
        print("Importação cancelada pelo usuário.")

    sys.exit(0)