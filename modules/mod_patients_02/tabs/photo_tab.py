from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path


class PhotoCard(QtWidgets.QWidget):
    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.titulo = titulo
        self.image_path = None
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.label_titulo = QtWidgets.QLabel(self.titulo)
        self.label_titulo.setAlignment(QtCore.Qt.AlignCenter)

        self.preview = QtWidgets.QLabel()
        self.preview.setFixedSize(140, 140)
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setStyleSheet("border: 1px solid #ccc; border-radius: 6px;")

        self._set_placeholder()

        self.btn = QtWidgets.QPushButton("Selecionar")
        self.btn.clicked.connect(self._selecionar_imagem)

        layout.addWidget(self.label_titulo)
        layout.addWidget(self.preview, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.btn, alignment=QtCore.Qt.AlignCenter)

    def _set_placeholder(self):
        icon_path = Path("resources/icons/photo.svg")
        if icon_path.exists():
            pix = QtGui.QPixmap(str(icon_path))
            self.preview.setPixmap(
                pix.scaled(70, 70, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            )
        else:
            self.preview.setText("Sem imagem")

    def _selecionar_imagem(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Selecionar imagem",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        self.image_path = file_path
        pix = QtGui.QPixmap(file_path)

        self.preview.setPixmap(
            pix.scaled(
                self.preview.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )

    def get_path(self):
        return self.image_path

    def set_path(self, path: str):
        if not path:
            self.image_path = None
            self._set_placeholder()
            return

        self.image_path = path
        pix = QtGui.QPixmap(path)

        self.preview.setPixmap(
            pix.scaled(
                self.preview.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )


class PhotoTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        container = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(container)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(16)

        box_face = QtWidgets.QGroupBox("Fotografias da face")
        layout_face = QtWidgets.QHBoxLayout(box_face)
        layout_face.setAlignment(QtCore.Qt.AlignCenter)
        layout_face.setSpacing(20)

        self.card_frontal = PhotoCard("Frontal")
        self.card_perfil = PhotoCard("Perfil")

        layout_face.addWidget(self.card_frontal)
        layout_face.addWidget(self.card_perfil)

        box_intra = QtWidgets.QGroupBox("Fotografias intrabucais")
        layout_intra = QtWidgets.QVBoxLayout(box_intra)
        layout_intra.setAlignment(QtCore.Qt.AlignCenter)
        layout_intra.setSpacing(14)

        row_oclusal = QtWidgets.QHBoxLayout()
        row_oclusal.setAlignment(QtCore.Qt.AlignCenter)
        row_oclusal.setSpacing(20)

        self.card_oclusal_sup = PhotoCard("Oclusal sup")
        self.card_oclusal_inf = PhotoCard("Oclusal inf")

        row_oclusal.addWidget(self.card_oclusal_sup)
        row_oclusal.addWidget(self.card_oclusal_inf)

        row_dent = QtWidgets.QHBoxLayout()
        row_dent.setAlignment(QtCore.Qt.AlignCenter)
        row_dent.setSpacing(20)

        self.card_dent_frontal = PhotoCard("Dentição frontal")
        self.card_dent_lat_dir = PhotoCard("Dentição lateral dir")
        self.card_dent_lat_esq = PhotoCard("Dentição lateral esq")

        row_dent.addWidget(self.card_dent_frontal)
        row_dent.addWidget(self.card_dent_lat_dir)
        row_dent.addWidget(self.card_dent_lat_esq)

        layout_intra.addLayout(row_oclusal)
        layout_intra.addLayout(row_dent)

        content_layout.addWidget(box_face)
        content_layout.addWidget(box_intra)
        content_layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def get_data(self):
        return {
            "frontal": self.card_frontal.get_path(),
            "perfil": self.card_perfil.get_path(),
            "oclusal_sup": self.card_oclusal_sup.get_path(),
            "oclusal_inf": self.card_oclusal_inf.get_path(),
            "dent_frontal": self.card_dent_frontal.get_path(),
            "dent_lat_dir": self.card_dent_lat_dir.get_path(),
            "dent_lat_esq": self.card_dent_lat_esq.get_path(),
        }

    def set_data(self, data: dict):
        self.card_frontal.set_path(data.get("frontal"))
        self.card_perfil.set_path(data.get("perfil"))
        self.card_oclusal_sup.set_path(data.get("oclusal_sup"))
        self.card_oclusal_inf.set_path(data.get("oclusal_inf"))
        self.card_dent_frontal.set_path(data.get("dent_frontal"))
        self.card_dent_lat_dir.set_path(data.get("dent_lat_dir"))
        self.card_dent_lat_esq.set_path(data.get("dent_lat_esq"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("PhotoTab - Teste")

    widget = PhotoTab()
    window.setCentralWidget(widget)

    window.resize(900, 500)
    window.show()

    sys.exit(app.exec())