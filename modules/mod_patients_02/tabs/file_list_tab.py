from PySide6 import QtWidgets, QtCore
from modules.mod_patients_02.ui_components import criar_linha_arquivo


class FileListTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self._init_ui()
        self._build_layout()

    def _init_ui(self):
        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_maxila = QtWidgets.QLineEdit()
        self.edit_mandibula = QtWidgets.QLineEdit()
        self.edit_face = QtWidgets.QLineEdit()

    def _build_layout(self):
        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()

        form.addRow("Tomografia:", criar_linha_arquivo(self.edit_tomografia, self._buscar_caminho, True))
        form.addRow("Scan Face:", criar_linha_arquivo(self.edit_face, self._buscar_caminho, False))
        form.addRow("Scan Maxila:", criar_linha_arquivo(self.edit_maxila, self._buscar_caminho, False))
        form.addRow("Scan Mandíbula:", criar_linha_arquivo(self.edit_mandibula, self._buscar_caminho, False))


        layout.addLayout(form)
        layout.addStretch()

    def _buscar_caminho(self, target, folder=True):
        settings = QtCore.QSettings("OpenCMF", "Config")

        chave = "ultimo_diretorio_dicom" if target == self.edit_tomografia else "ultimo_diretorio_geral"
        ultimo = settings.value(chave, "")

        if folder:
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecionar Pasta", ultimo)
        else:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Selecionar Arquivo",
                ultimo,
                "Malhas (*.stl *.obj *.ply)"
            )

        if path:
            target.setText(path)
            settings.setValue(chave, path)

    def get_data(self):
        return {
            "dicom": self.edit_tomografia.text(),
            "maxila": self.edit_maxila.text(),
            "mandibula": self.edit_mandibula.text(),
            "face": self.edit_face.text(),
        }

    def set_data(self, data: dict):
        self.edit_tomografia.setText(data.get("dicom", ""))
        self.edit_face.setText(data.get("face", ""))
        self.edit_maxila.setText(data.get("maxila", ""))
        self.edit_mandibula.setText(data.get("mandibula", ""))
