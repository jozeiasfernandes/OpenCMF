import shutil
import zipfile
import os
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui


class ProjectTab(QtWidgets.QWidget):
    importacao_concluida = QtCore.Signal()

    def __init__(self, project_manager=None):
        super().__init__()
        self.project_manager = project_manager
        self.pasta_paciente = None
        self._init_ui()
        self._build_layout()

    def _init_ui(self):
        self.label_status = QtWidgets.QLabel("Gerenciamento de Pacotes e Arquivos")
        self.label_status.setAlignment(QtCore.Qt.AlignCenter)
        self.label_status.setStyleSheet("font-weight: bold; colors: #555; font-size: 14px;")

        self.btn_abrir_pasta = QtWidgets.QPushButton("Abrir Pasta do Projeto")
        self.btn_abrir_pasta.setMinimumHeight(40)
        self.btn_abrir_pasta.clicked.connect(self._abrir_pasta_paciente)

        self.btn_exportar = QtWidgets.QPushButton("Exportar Projeto (.zip)")
        self.btn_exportar.setMinimumHeight(40)
        self.btn_exportar.clicked.connect(self._executar_exportacao)

        self.btn_importar = QtWidgets.QPushButton("Importar Projeto (.zip)")
        self.btn_importar.setMinimumHeight(40)
        self.btn_importar.clicked.connect(self._executar_importacao)

        self.model = QtWidgets.QFileSystemModel()
        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)

        for i in range(1, 4):
            self.tree.hideColumn(i)

        self.label_tamanho = QtWidgets.QLabel("Tamanho total: 0 KB")
        self.label_tamanho.setAlignment(QtCore.Qt.AlignRight)

    def _build_layout(self):
        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(self.label_status)
        layout.addSpacing(10)

        layout_botoes = QtWidgets.QHBoxLayout()
        layout_botoes.addWidget(self.btn_abrir_pasta)
        layout_botoes.addWidget(self.btn_exportar)
        layout_botoes.addWidget(self.btn_importar)
        layout.addLayout(layout_botoes)

        layout.addSpacing(10)
        layout.addWidget(QtWidgets.QLabel("Arquivos no diretório do paciente:"))
        layout.addWidget(self.tree)
        layout.addWidget(self.label_tamanho)

    def set_data(self, data: dict, pasta: str = None):
        self.pasta_paciente = pasta
        if pasta:
            path_obj = Path(pasta).absolute()
            nome = path_obj.name
            self.label_status.setText(f"Paciente: {nome}")

            abs_path = str(path_obj)
            index = self.model.setRootPath(abs_path)
            self.tree.setRootIndex(index)

            self._atualizar_label_tamanho(path_obj)

    def _atualizar_label_tamanho(self, path_obj):
        bytes_size = sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                break
            bytes_size /= 1024.0

        self.label_tamanho.setText(f"Tamanho total: {bytes_size:.2f} {unit}")

    def _abrir_pasta_paciente(self):
        if not self.pasta_paciente:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um paciente primeiro.")
            return

        path = QtCore.QUrl.fromLocalFile(str(Path(self.pasta_paciente).absolute()))
        QtGui.QDesktopServices.openUrl(path)

    def _executar_exportacao(self):
        if not self.pasta_paciente:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um paciente primeiro.")
            return

        origem = Path(self.pasta_paciente)
        sugestao = f"{origem.name}.zip"

        destino_zip, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Exportar Projeto", sugestao, "Zip files (*.zip)"
        )

        if not destino_zip:
            return

        try:
            base = str(Path(destino_zip).with_suffix(''))
            shutil.make_archive(base, 'zip', origem)
            QtWidgets.QMessageBox.information(self, "Sucesso", "Exportação concluída.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Falha ao exportar: {str(e)}")

    def _executar_importacao(self):
        settings = QtCore.QSettings("OpenCMF", "Config")
        ultimo_dir = settings.value("ultimo_diretorio_zip", "")

        zip_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Importar Projeto", ultimo_dir, "Zip files (*.zip)"
        )

        if not zip_path:
            return

        settings.setValue("ultimo_diretorio_zip", str(Path(zip_path).parent))
        destino_base = Path("pacients")
        destino_base.mkdir(exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                nome_pasta = Path(zip_path).stem
                caminho_final = destino_base / nome_pasta

                if caminho_final.exists():
                    msg = f"A pasta '{nome_pasta}' já existe. Deseja sobrescrever?"
                    res = QtWidgets.QMessageBox.question(self, "Confirmar", msg)
                    if res == QtWidgets.QMessageBox.No:
                        return
                    shutil.rmtree(caminho_final)

                zip_ref.extractall(caminho_final)
                QtWidgets.QMessageBox.information(self, "Sucesso", "Importação concluída.")
                self.importacao_concluida.emit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Falha ao importar: {str(e)}")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    base_teste = Path("pacients/Paciente_Teste")
    base_teste.mkdir(parents=True, exist_ok=True)
    (base_teste / "surfaces").mkdir(exist_ok=True)
    (base_teste / "surfaces/mandibula.stl").write_text("dummy mesh")
    (base_teste / "info.json").write_text("{}")

    window = ProjectTab()
    window.set_data({}, str(base_teste.absolute()))
    window.resize(700, 500)
    window.show()

    sys.exit(app.exec())