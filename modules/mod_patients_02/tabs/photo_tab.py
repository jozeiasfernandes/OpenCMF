from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui


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
            self, "Selecionar imagem", "", "Imagens (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.set_path(file_path)

    def get_path(self):
        return self.image_path

    def set_path(self, path: str):
        if not path:
            self.image_path = None
            self._set_placeholder()
            return

        self.image_path = str(Path(path).resolve())
        pix = QtGui.QPixmap(self.image_path)
        self.preview.setPixmap(
            pix.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        )


class PhotoTab(QtWidgets.QWidget):
    salvamento_solicitado = QtCore.Signal()

    def __init__(self, project_manager=None):
        super().__init__()
        self.project_manager = project_manager
        self.pasta_paciente = None
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
        row_oclusal.setSpacing(20)
        self.card_oclusal_sup = PhotoCard("Oclusal sup")
        self.card_oclusal_inf = PhotoCard("Oclusal inf")
        row_oclusal.addWidget(self.card_oclusal_sup)
        row_oclusal.addWidget(self.card_oclusal_inf)

        row_dent = QtWidgets.QHBoxLayout()
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

        self.btn_salvar = QtWidgets.QPushButton("Salvar Fotografias")
        self.btn_salvar.setMinimumHeight(45)
        self.btn_salvar.clicked.connect(self._executar_salvamento)
        content_layout.addWidget(self.btn_salvar)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _executar_salvamento(self):
        if not self.pasta_paciente or not self.project_manager:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Identifique o paciente primeiro.")
            return

        root = Path(self.pasta_paciente)
        data = self.project_manager.load_project(root) or {}
        data["fotos"] = self.get_data()

        if self.project_manager.save_project(root, data):
            QtWidgets.QMessageBox.information(self, "Sucesso", "Fotografias salvas.")
            self.salvamento_solicitado.emit()

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

    def set_data(self, data: dict, pasta: str = None):
        if pasta:
            self.pasta_paciente = pasta

        fotos = data.get("fotos", {})
        self.card_frontal.set_path(fotos.get("frontal"))
        self.card_perfil.set_path(fotos.get("perfil"))
        self.card_oclusal_sup.set_path(fotos.get("oclusal_sup"))
        self.card_oclusal_inf.set_path(fotos.get("oclusal_inf"))
        self.card_dent_frontal.set_path(fotos.get("dent_frontal"))
        self.card_dent_lat_dir.set_path(fotos.get("dent_lat_dir"))
        self.card_dent_lat_esq.set_path(fotos.get("dent_lat_esq"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(PhotoTab())
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec())