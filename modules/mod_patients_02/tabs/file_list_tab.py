from pathlib import Path
from PySide6 import QtWidgets, QtCore
from modules.mod_patients_02.ui_components import criar_linha_arquivo


class FileListTab(QtWidgets.QWidget):
    salvamento_solicitado = QtCore.Signal()

    def __init__(self, project_manager=None):
        super().__init__()
        self.project_manager = project_manager
        self.pasta_paciente = None

        self._init_ui()
        self._build_layout()

    def _init_ui(self):
        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_maxila = QtWidgets.QLineEdit()
        self.edit_mandibula = QtWidgets.QLineEdit()
        self.edit_face = QtWidgets.QLineEdit()

        self.btn_salvar = QtWidgets.QPushButton("Salvar lista de caminhos")
        self.btn_salvar.setMinimumHeight(45)
        self.btn_salvar.clicked.connect(self._executar_salvamento)

    def _build_layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        form.addRow("Tomografia:", criar_linha_arquivo(self.edit_tomografia, self._buscar_caminho, True))
        form.addRow("Scan Face:", criar_linha_arquivo(self.edit_face, self._buscar_caminho, False))
        form.addRow("Scan Maxila:", criar_linha_arquivo(self.edit_maxila, self._buscar_caminho, False))
        form.addRow("Scan Mandíbula:", criar_linha_arquivo(self.edit_mandibula, self._buscar_caminho, False))

        layout.addLayout(form)
        layout.addStretch()
        layout.addWidget(self.btn_salvar)

    def _buscar_caminho(self, target, folder=True):
        settings = QtCore.QSettings("OpenCMF", "Config")
        chave = "ultimo_diretorio_dicom" if target == self.edit_tomografia else "ultimo_diretorio_geral"
        ultimo = settings.value(chave, "")

        if folder:
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecionar Pasta", ultimo)
        else:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Selecionar Arquivo", ultimo, "Malhas (*.stl *.obj *.ply)"
            )

        if path:
            target.setText(path)
            settings.setValue(chave, path)

    def _executar_salvamento(self):
        if not self.pasta_paciente or not self.project_manager:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Salve os dados pessoais primeiro.")
            return

        root = Path(self.pasta_paciente)
        data = self.project_manager.load_project(root) or {}
        data["caminhos"] = self.get_data()

        if self.project_manager.save_project(root, data):
            QtWidgets.QMessageBox.information(self, "Sucesso", "Caminhos de arquivos salvos.")
            self.salvamento_solicitado.emit()
        else:
            QtWidgets.QMessageBox.critical(self, "Erro", "Falha ao salvar arquivos.")

    def get_data(self) -> dict:
        return {
            "dicom": self.edit_tomografia.text(),
            "maxila": self.edit_maxila.text(),
            "mandibula": self.edit_mandibula.text(),
            "face": self.edit_face.text(),
        }

    def set_data(self, data: dict, pasta: str = None):
        if pasta:
            self.pasta_paciente = pasta

        caminhos = data.get("caminhos", {})
        self.edit_tomografia.setText(caminhos.get("dicom", ""))
        self.edit_maxila.setText(caminhos.get("maxila", ""))
        self.edit_mandibula.setText(caminhos.get("mandibula", ""))
        self.edit_face.setText(caminhos.get("face", ""))