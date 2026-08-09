import shutil
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui


class PhotoCard(QtWidgets.QWidget):
    foto_alterada = QtCore.Signal(str)

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
        self.btn.clicked.connect(self._ao_clicar_selecionar)

        layout.addWidget(self.label_titulo)
        layout.addWidget(self.preview, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.btn, alignment=QtCore.Qt.AlignCenter)

    def _set_placeholder(self):
        icon_path = Path("resources/icons_manager/photo.svg")
        if icon_path.exists():
            pix = QtGui.QPixmap(str(icon_path))
            self.preview.setPixmap(
                pix.scaled(70, 70, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            )
        else:
            self.preview.setText("Sem imagem")

    def _ao_clicar_selecionar(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Selecionar imagem", "", "Imagens (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.foto_alterada.emit(file_path)

    def get_path(self):
        return self.image_path

    def set_path(self, path: str):
        if not path or not Path(path).exists():
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
        self._cards = {}
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
        layout_face.setSpacing(20)

        self._cards["frontal"] = PhotoCard("Frontal")
        self._cards["perfil"] = PhotoCard("Perfil")

        box_intra = QtWidgets.QGroupBox("Fotografias intrabucais")
        layout_intra = QtWidgets.QVBoxLayout(box_intra)
        layout_intra.setSpacing(14)

        row_oclusal = QtWidgets.QHBoxLayout()
        self._cards["oclusal_sup"] = PhotoCard("Oclusal sup")
        self._cards["oclusal_inf"] = PhotoCard("Oclusal inf")

        row_dent = QtWidgets.QHBoxLayout()
        self._cards["dent_frontal"] = PhotoCard("Dentição frontal")
        self._cards["dent_lat_dir"] = PhotoCard("Dentição lateral dir")
        self._cards["dent_lat_esq"] = PhotoCard("Dentição lateral esq")

        for chave, card in self._cards.items():
            card.foto_alterada.connect(lambda path, k=chave: self._processar_importacao(k, path))

        layout_face.addWidget(self._cards["frontal"])
        layout_face.addWidget(self._cards["perfil"])

        row_oclusal.addWidget(self._cards["oclusal_sup"])
        row_oclusal.addWidget(self._cards["oclusal_inf"])

        row_dent.addWidget(self._cards["dent_frontal"])
        row_dent.addWidget(self._cards["dent_lat_dir"])
        row_dent.addWidget(self._cards["dent_lat_esq"])

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

    def _processar_importacao(self, chave: str, origem: str):
        if not self.pasta_paciente:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um paciente primeiro.")
            return

        diretorio_fotos = Path(self.pasta_paciente) / "photos"
        diretorio_fotos.mkdir(parents=True, exist_ok=True)

        extensao = Path(origem).suffix.lower()
        destino = diretorio_fotos / f"{chave}{extensao}"

        try:
            shutil.copy2(origem, destino)
            self._cards[chave].set_path(str(destino))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Falha ao copiar imagem: {e}")

    def _executar_salvamento(self):
        if not self.pasta_paciente or not self.project_manager:
            return

        root = Path(self.pasta_paciente)
        data = self.project_manager.load_project(root) or {}
        data["fotos"] = self.get_data()

        if self.project_manager.save_project(root, data):
            self.salvamento_solicitado.emit()

    def get_data(self):
        return {chave: card.get_path() for chave, card in self._cards.items()}

    def set_data(self, data: dict, pasta: str = None):
        if pasta:
            self.pasta_paciente = pasta

        fotos = data.get("fotos", {})
        for chave, card in self._cards.items():
            card.set_path(fotos.get(chave))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(PhotoTab())
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec())