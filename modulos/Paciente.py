import json
import time
from datetime import date
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.base import ModuloBase

PASTA_PACIENTES = Path("pacientes")


class SecaoRetratil(QtWidgets.QWidget):
    """Widget customizado para seções que expandem e recolhem."""

    def __init__(self, titulo, inicial_aberto=False, parent=None):
        super().__init__(parent)
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 5, 0, 5)
        self.layout_principal.setSpacing(0)

        self.botao_toggle = QtWidgets.QPushButton(f"{'▼' if inicial_aberto else '▶'}  {titulo}")
        self.botao_toggle.setCheckable(True)
        self.botao_toggle.setChecked(inicial_aberto)
        self.botao_toggle.setStyleSheet("""
            QPushButton {
                text-align: left; padding: 8px; font-weight: bold;
                background-color: #2c3e50; color: white; border: 1px solid #34495e; border-radius: 4px;
            }
            QPushButton:checked { border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; }
        """)

        self.conteudo = QtWidgets.QWidget()
        self.conteudo.setVisible(inicial_aberto)
        self.layout_conteudo = QtWidgets.QVBoxLayout(self.conteudo)
        self.layout_conteudo.setContentsMargins(10, 10, 10, 10)

        self.layout_principal.addWidget(self.botao_toggle)
        self.layout_principal.addWidget(self.conteudo)
        self.botao_toggle.toggled.connect(self.ao_alternar)

    def ao_alternar(self, checked):
        self.conteudo.setVisible(checked)
        texto = self.botao_toggle.text()[2:]
        self.botao_toggle.setText(f"{'▼' if checked else '▶'}  {texto}")

    def layout_interno(self):
        return self.layout_conteudo


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.pasta_paciente = None
        PASTA_PACIENTES.mkdir(exist_ok=True)
        self.main_container = QtWidgets.QWidget()
        self._init_ui_components()

    def _init_ui_components(self):
        # --- Dados Principais ---
        self.edit_nome = QtWidgets.QLineEdit()
        self.edit_nome.setPlaceholderText("Nome completo...")

        self.edit_cpf = QtWidgets.QLineEdit()
        self.edit_cpf.setPlaceholderText("000.000.000-00")

        self.edit_email = QtWidgets.QLineEdit()
        self.edit_email.setPlaceholderText("exemplo@email.com")

        self.edit_nascimento = QtWidgets.QDateEdit(calendarPopup=True)
        self.edit_nascimento.setDisplayFormat("dd/MM/yyyy")
        self.edit_nascimento.setDate(QtCore.QDate.currentDate())

        self.combo_sexo = QtWidgets.QComboBox()
        self.combo_sexo.addItems(["Masculino", "Feminino", "Outro"])

        # --- Endereço ---
        self.edit_logradouro = QtWidgets.QLineEdit()
        self.edit_cidade = QtWidgets.QLineEdit()
        self.edit_estado = QtWidgets.QLineEdit()

        # --- Dados Clínicos ---
        self.edit_diagnostico = QtWidgets.QTextEdit()
        self.edit_diagnostico.setMaximumHeight(80)
        self.edit_alergias = QtWidgets.QLineEdit()

        # --- Arquivos ---
        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_maxila = QtWidgets.QLineEdit()
        self.edit_mandibula = QtWidgets.QLineEdit()
        self.edit_face = QtWidgets.QLineEdit()

        self.btn_salvar = QtWidgets.QPushButton("Salvar Projeto")

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.pasta_paciente = caminho_paciente
        path_json = Path(caminho_paciente) / "projeto" / "info.json"

        if path_json.exists():
            try:
                with open(path_json, "r", encoding="utf-8") as f:
                    dados = json.load(f)

                p = dados.get("paciente", {})
                e = dados.get("endereco", {})
                c = dados.get("clinico", {})
                paths = dados.get("caminhos", {})

                # Set Dados Principais
                self.edit_nome.setText(p.get("nome", ""))
                self.edit_cpf.setText(p.get("cpf", ""))
                self.edit_email.setText(p.get("email", ""))
                self.combo_sexo.setCurrentText(p.get("sexo", "Masculino"))
                if p.get("nascimento"):
                    self.edit_nascimento.setDate(QtCore.QDate.fromString(p["nascimento"], "yyyy-MM-dd"))

                # Set Endereço
                self.edit_logradouro.setText(e.get("logradouro", ""))
                self.edit_cidade.setText(e.get("cidade", ""))
                self.edit_estado.setText(e.get("estado", ""))

                # Set Clínico
                self.edit_diagnostico.setPlainText(c.get("diagnostico", ""))
                self.edit_alergias.setText(c.get("alergias", ""))

                # Set Arquivos
                self.edit_tomografia.setText(paths.get("dicom", ""))
                self.edit_maxila.setText(paths.get("maxila", ""))
                self.edit_mandibula.setText(paths.get("mandibula", ""))
                self.edit_face.setText(paths.get("face", ""))

            except Exception as e:
                print(f"Erro carga: {e}")

    def _processar_cadastro(self):
        nome = self.edit_nome.text().strip()
        if not nome:
            QtWidgets.QMessageBox.warning(self.main_container, "Atenção", "O nome é obrigatório.")
            return

        try:
            if self.pasta_paciente and Path(self.pasta_paciente).exists():
                diretorio = Path(self.pasta_paciente)
            else:
                projeto_id = f"PRJ_{int(time.time())}_{nome.replace(' ', '_').upper()}"
                diretorio = PASTA_PACIENTES / projeto_id

            for sub in ["projeto", "modulo_tomografia", "modulo_osteotomia"]:
                (diretorio / sub).mkdir(parents=True, exist_ok=True)

            info_path = diretorio / "projeto" / "info.json"
            dados_finais = {}
            if info_path.exists():
                with open(info_path, "r", encoding="utf-8") as f: dados_finais = json.load(f)

            dados_finais["paciente"] = {
                "nome": nome,
                "cpf": self.edit_cpf.text(),
                "email": self.edit_email.text(),
                "nascimento": self.edit_nascimento.date().toString("yyyy-MM-dd"),
                "sexo": self.combo_sexo.currentText()
            }
            dados_finais["endereco"] = {
                "logradouro": self.edit_logradouro.text(),
                "cidade": self.edit_cidade.text(),
                "estado": self.edit_estado.text()
            }
            dados_finais["clinico"] = {
                "diagnostico": self.edit_diagnostico.toPlainText(),
                "alergias": self.edit_alergias.text()
            }

            if "caminhos" not in dados_finais: dados_finais["caminhos"] = {}
            dados_finais["caminhos"].update({
                "workspace": str(diretorio.absolute()),
                "dicom": self.edit_tomografia.text(),
                "maxila": self.edit_maxila.text(),
                "mandibula": self.edit_mandibula.text(),
                "face": self.edit_face.text()
            })

            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(dados_finais, f, indent=4, ensure_ascii=False)

            self.pasta_paciente = str(diretorio)
            QtWidgets.QMessageBox.information(self.main_container, "Sucesso", "Dados salvos!")
            self.concluido.emit()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_container, "Erro", str(e))

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.main_container.layout(): return self.main_container

        layout = QtWidgets.QVBoxLayout(self.main_container)

        # --- 1. Informações do Paciente (Dados Principais) ---
        group_pessoal = QtWidgets.QGroupBox("Informações do Paciente")
        layout_pessoal = QtWidgets.QVBoxLayout(group_pessoal)

        # 1ª Linha: Nome
        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(QtWidgets.QLabel("Nome:"))
        row1.addWidget(self.edit_nome)
        layout_pessoal.addLayout(row1)

        # 2ª Linha: CPF e E-mail
        row2 = QtWidgets.QHBoxLayout()
        row2.addWidget(QtWidgets.QLabel("CPF:"))
        row2.addWidget(self.edit_cpf)
        row2.addSpacing(10)
        row2.addWidget(QtWidgets.QLabel("E-mail:"))
        row2.addWidget(self.edit_email)
        layout_pessoal.addLayout(row2)

        # 3ª Linha: Nascimento e Sexo
        row3 = QtWidgets.QHBoxLayout()
        row3.addWidget(QtWidgets.QLabel("Nascimento:"))
        row3.addWidget(self.edit_nascimento)
        row3.addSpacing(10)
        row3.addWidget(QtWidgets.QLabel("Sexo:"))
        row3.addWidget(self.combo_sexo)
        row3.addStretch()
        layout_pessoal.addLayout(row3)

        layout.addWidget(group_pessoal)

        # --- 2. Seção Endereço (Oculta) ---
        secao_end = SecaoRetratil("ENDEREÇO", False)
        form_end = QtWidgets.QFormLayout()
        form_end.addRow("Logradouro:", self.edit_logradouro)
        form_end.addRow("Cidade:", self.edit_cidade)
        form_end.addRow("Estado:", self.edit_estado)
        secao_end.layout_interno().addLayout(form_end)
        layout.addWidget(secao_end)

        # --- 3. Seção Dados Clínicos (Oculta) ---
        secao_clin = SecaoRetratil("DADOS CLÍNICOS", False)
        form_clin = QtWidgets.QFormLayout()
        form_clin.addRow("Diagnóstico:", self.edit_diagnostico)
        form_clin.addRow("Alergias:", self.edit_alergias)
        secao_clin.layout_interno().addLayout(form_clin)
        layout.addWidget(secao_clin)

        # --- 4. Arquivos Base ---
        group_arq = QtWidgets.QGroupBox("Arquivos Base")
        form_arq = QtWidgets.QFormLayout(group_arq)
        form_arq.addRow("Tomografia:", self._criar_linha_arquivo(self.edit_tomografia, True))
        form_arq.addRow("STL Maxila:", self._criar_linha_arquivo(self.edit_maxila, False))
        form_arq.addRow("STL Mandíbula:", self._criar_linha_arquivo(self.edit_mandibula, False))
        form_arq.addRow("STL Face:", self._criar_linha_arquivo(self.edit_face, False))
        layout.addWidget(group_arq)

        self.btn_salvar.setMinimumHeight(40)
        self.btn_salvar.clicked.connect(self._processar_cadastro)
        layout.addStretch()
        layout.addWidget(self.btn_salvar)

        return self.main_container

    def _criar_linha_arquivo(self, line_edit, folder=True):
        widget = QtWidgets.QWidget()
        lay = QtWidgets.QHBoxLayout(widget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(line_edit)
        btn = QtWidgets.QToolButton()
        btn.setText("...")
        btn.clicked.connect(lambda: self._buscar_caminho(line_edit, folder))
        lay.addWidget(btn)
        return widget

    def _buscar_caminho(self, target_edit, folder=True):
        if folder:
            path = QtWidgets.QFileDialog.getExistingDirectory(self.main_container, "Pasta")
        else:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self.main_container, "Arquivo", "",
                                                            "Malhas (*.stl *.obj *.ply)")
        if path: target_edit.setText(path)

    def get_toolbox(self):
        return QtWidgets.QWidget()