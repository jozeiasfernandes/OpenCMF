import shutil
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
                self, "Selecionar Arquivo", ultimo, "Malhas (*.stl *.obj *.ply *.vtk *.vtp)"
            )

        if path:
            path_final = self._gerenciar_copia_arquivo(target, path)
            target.setText(path_final)
            settings.setValue(chave, path)

    def _gerenciar_copia_arquivo(self, target, caminho_origem: str) -> str:
        if not self.pasta_paciente or target == self.edit_tomografia:
            return caminho_origem

        origem = Path(caminho_origem)
        if not origem.is_file():
            return caminho_origem

        pasta_destino = Path(self.pasta_paciente) / "surfaces"
        pasta_destino.mkdir(parents=True, exist_ok=True)

        arquivo_destino = pasta_destino / origem.name

        if arquivo_destino.exists():
            if arquivo_destino.samefile(origem):
                return str(arquivo_destino)

            resposta = QtWidgets.QMessageBox.question(
                self,
                "Arquivo Existente",
                f"O arquivo '{origem.name}' já existe na pasta do paciente.\nDeseja sobrescrevê-lo?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if resposta == QtWidgets.QMessageBox.No:
                return target.text()

        try:
            shutil.copy2(origem, arquivo_destino)
            return str(arquivo_destino)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erro", f"Falha na cópia: {e}")
            return caminho_origem

    def _executar_salvamento(self):
        if not self.pasta_paciente or not self.project_manager:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Identifique o paciente primeiro.")
            return

        root = Path(self.pasta_paciente)
        data = self.project_manager.load_project(root) or {}

        caminhos = data.get("caminhos", {})
        caminhos.update(self.get_data())
        data["caminhos"] = caminhos

        if self.project_manager.save_project(root, data):
            QtWidgets.QMessageBox.information(self, "Sucesso", "Caminhos de arquivos salvos com sucesso.")
            self.salvamento_solicitado.emit()
        else:
            QtWidgets.QMessageBox.critical(self, "Erro", "Não foi possível salvar os caminhos.")

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

        c = data.get("caminhos", {})
        self.edit_tomografia.setText(c.get("dicom", ""))
        self.edit_maxila.setText(c.get("maxila", ""))
        self.edit_mandibula.setText(c.get("mandibula", ""))
        self.edit_face.setText(c.get("face", ""))