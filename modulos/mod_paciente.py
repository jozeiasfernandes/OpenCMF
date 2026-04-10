import json
import time
from datetime import date
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from core.base import ModuloBase

PASTA_PACIENTES = Path("pacientes")


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.pasta_paciente = None
        PASTA_PACIENTES.mkdir(exist_ok=True)
        self._init_ui_components()

    def _init_ui_components(self):
        # --- Dados Pessoais ---
        self.edit_nome = QtWidgets.QLineEdit()
        self.edit_nome.setPlaceholderText("Nome completo...")

        self.edit_nascimento = QtWidgets.QDateEdit()
        self.edit_nascimento.setCalendarPopup(True)
        self.edit_nascimento.setDisplayFormat("dd/MM/yyyy")
        self.edit_nascimento.setDate(QtCore.QDate.currentDate())

        self.combo_sexo = QtWidgets.QComboBox()
        self.combo_sexo.addItems(["Masculino", "Feminino", "Outro"])

        # --- Arquivos ---
        self.edit_raiz = QtWidgets.QLineEdit()  # workspace
        self.edit_dicom = QtWidgets.QLineEdit()
        self.edit_maxila = QtWidgets.QLineEdit()
        self.edit_mandibula = QtWidgets.QLineEdit()
        self.edit_face = QtWidgets.QLineEdit()

    def _criar_linha_arquivo(self, label, line_edit):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(line_edit)

        btn_buscar = QtWidgets.QToolButton()
        btn_buscar.setText("...")

        if line_edit in [self.edit_raiz, self.edit_dicom]:
            btn_buscar.clicked.connect(lambda: self._buscar_caminho(line_edit, folder=True))
        else:
            btn_buscar.clicked.connect(lambda: self._buscar_caminho(line_edit, folder=False))

        layout.addWidget(btn_buscar)
        return layout

    def _buscar_caminho(self, target_edit, folder=True):
        if folder:
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        else:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Selecionar Arquivo", "", "Malhas (*.stl *.obj *.ply)"
            )
        if path:
            target_edit.setText(path)

    def get_workspace(self) -> QtWidgets.QWidget:
        workspace = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(workspace)

        frame_pessoais = QtWidgets.QGroupBox("Dados do Paciente")
        layout_pessoais = QtWidgets.QFormLayout(frame_pessoais)
        layout_pessoais.addRow("Nome:", self.edit_nome)

        linha_detalhes = QtWidgets.QHBoxLayout()
        linha_detalhes.addWidget(self.edit_nascimento, stretch=2)
        linha_detalhes.addWidget(QtWidgets.QLabel("Sexo:"))
        linha_detalhes.addWidget(self.combo_sexo, stretch=1)

        layout_pessoais.addRow("Nascimento:", linha_detalhes)

        frame_arquivos = QtWidgets.QGroupBox("Arquivos")
        layout_form = QtWidgets.QFormLayout(frame_arquivos)

        layout_form.addRow("Workspace:", self._criar_linha_arquivo("", self.edit_raiz))
        layout_form.addRow("DICOM:", self._criar_linha_arquivo("", self.edit_dicom))
        layout_form.addRow("Maxila:", self._criar_linha_arquivo("", self.edit_maxila))
        layout_form.addRow("Mandíbula:", self._criar_linha_arquivo("", self.edit_mandibula))
        layout_form.addRow("Face:", self._criar_linha_arquivo("", self.edit_face))

        self.btn_salvar = QtWidgets.QPushButton("Salvar Projeto")
        self.btn_salvar.clicked.connect(self._processar_cadastro)

        main_layout.addWidget(frame_pessoais)
        main_layout.addWidget(frame_arquivos)
        main_layout.addWidget(self.btn_salvar)

        return workspace

    def get_toolbox(self):
        toolbox = QtWidgets.QWidget()
        toolbox.setVisible(False)
        return toolbox

    def _processar_cadastro(self):
        nome_raw = self.edit_nome.text().strip()
        workspace_input = self.edit_raiz.text().strip()

        if not nome_raw or not workspace_input:
            QtWidgets.QMessageBox.warning(
                self, "Aviso", "Nome e Workspace são obrigatórios."
            )
            return

        try:
            # --- Idade ---
            data_nasc = self.edit_nascimento.date().toPython()
            hoje = date.today()
            idade = hoje.year - data_nasc.year - (
                (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day)
            )

            # --- ID ---
            timestamp = int(time.time())
            nome_slug = nome_raw.replace(" ", "_").upper()
            projeto_id = f"PRJ_{timestamp}_{nome_slug}"

            # --- Diretório INDEX (fixo) ---
            projeto_dir = PASTA_PACIENTES / projeto_id
            projeto_dir.mkdir(parents=True, exist_ok=True)

            # --- Workspace (flexível) ---
            workspace_path = Path(workspace_input) / nome_slug
            workspace_path.mkdir(parents=True, exist_ok=True)

            # --- JSON ---
            dados_projeto = {
                "id": projeto_id,
                "data_criacao": QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate),
                "paciente": {
                    "nome": nome_raw,
                    "nascimento": self.edit_nascimento.date().toString("yyyy-MM-dd"),
                    "idade": idade,
                    "sexo": self.combo_sexo.currentText(),
                },
                "caminhos": {
                    "workspace": str(workspace_path),
                    "dicom": self.edit_dicom.text(),
                    "maxila": self.edit_maxila.text(),
                    "mandibula": self.edit_mandibula.text(),
                    "face": self.edit_face.text(),
                },
                "status": "Em Planejamento",
            }

            # --- Salvar no índice ---
            arquivo_info = projeto_dir / "info.json"
            with open(arquivo_info, "w", encoding="utf-8") as f:
                json.dump(dados_projeto, f, indent=4, ensure_ascii=False)

            self.pasta_paciente = str(projeto_dir)

            QtWidgets.QMessageBox.information(
                self,
                "Sucesso",
                f"Projeto criado para {nome_raw} ({idade} anos).",
            )

            self.concluido.emit()

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Erro", f"Erro ao salvar projeto:\n{str(e)}"
            )