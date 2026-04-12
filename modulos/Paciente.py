import json
import time
import re
import requests
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
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
        self.edit_cpf.setInputMask("000.000.000-00;_")
        self.check_estrangeiro = QtWidgets.QCheckBox("Estrangeiro")
        self.check_estrangeiro.stateChanged.connect(self._toggle_estrangeiro)
        self.edit_email = QtWidgets.QLineEdit()
        self.edit_celular = QtWidgets.QLineEdit()
        self.edit_celular.setInputMask("(00) 00000-0000;_")
        self.edit_nascimento = QtWidgets.QDateEdit(calendarPopup=True)
        self.edit_nascimento.setDisplayFormat("dd/MM/yyyy")
        self.edit_nascimento.setDate(QtCore.QDate.currentDate())
        self.combo_sexo = QtWidgets.QComboBox()
        self.combo_sexo.addItems(["Masculino", "Feminino", "Outro"])

        # --- Endereço ---
        self.edit_cep = QtWidgets.QLineEdit()
        self.edit_cep.setInputMask("00000-000;_")
        self.btn_buscar_cep = QtWidgets.QPushButton("Buscar")
        self.btn_buscar_cep.clicked.connect(self._buscar_cep)
        self.edit_logradouro = QtWidgets.QLineEdit()
        self.edit_cidade = QtWidgets.QLineEdit()
        self.edit_estado = QtWidgets.QLineEdit()
        self.edit_pais = QtWidgets.QLineEdit()
        self.edit_pais.setText("Brasil")

        # --- Dados Clínicos ---
        self.edit_diagnostico = QtWidgets.QLineEdit()
        self.edit_historia_medica = QtWidgets.QTextEdit()
        self.edit_historia_medica.setMaximumHeight(60)
        self.edit_alergias = QtWidgets.QLineEdit()
        self.edit_medicacoes = QtWidgets.QLineEdit()
        self.edit_habitos = QtWidgets.QLineEdit()
        self.edit_planejamento = QtWidgets.QTextEdit()
        self.edit_planejamento.setMaximumHeight(80)

        # --- Arquivos ---
        self.edit_fotos = QtWidgets.QLineEdit()  # Adicionado
        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_maxila = QtWidgets.QLineEdit()
        self.edit_mandibula = QtWidgets.QLineEdit()
        self.edit_face = QtWidgets.QLineEdit()

        self.btn_salvar = QtWidgets.QPushButton("Salvar Projeto")

    def _toggle_estrangeiro(self, state):
        is_estrangeiro = state == QtCore.Qt.Checked.value
        self.edit_cpf.setEnabled(not is_estrangeiro)
        if is_estrangeiro:
            self.edit_cpf.setInputMask("")
            self.edit_cpf.setText("ISENTO")
            self.edit_pais.setText("")
        else:
            self.edit_cpf.setInputMask("000.000.000-00;_")
            self.edit_cpf.clear()
            self.edit_pais.setText("Brasil")

    def _buscar_cep(self):
        cep = re.sub(r'\D', '', self.edit_cep.text())
        if len(cep) != 8: return
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            if response.status_code == 200 and "erro" not in response.json():
                dados = response.json()
                self.edit_logradouro.setText(dados.get("logradouro", ""))
                self.edit_cidade.setText(dados.get("localidade", ""))
                self.edit_estado.setText(dados.get("uf", ""))
                self.edit_pais.setText("Brasil")
        except:
            pass

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.pasta_paciente = caminho_paciente
        path_json = Path(caminho_paciente) / "projeto" / "info.json"

        if path_json.exists():
            try:
                with open(path_json, "r", encoding="utf-8") as f:
                    d = json.load(f)

                p, e, c, paths = d.get("paciente", {}), d.get("endereco", {}), d.get("clinico", {}), d.get("caminhos",
                                                                                                           {})

                self.edit_nome.setText(p.get("nome", ""))
                self.edit_cpf.setText(p.get("cpf", ""))
                self.check_estrangeiro.setChecked(p.get("estrangeiro", False))
                self.edit_email.setText(p.get("email", ""))
                self.edit_celular.setText(p.get("celular", ""))
                self.combo_sexo.setCurrentText(p.get("sexo", "Masculino"))
                if p.get("nascimento"):
                    self.edit_nascimento.setDate(QtCore.QDate.fromString(p["nascimento"], "yyyy-MM-dd"))

                self.edit_cep.setText(e.get("cep", ""))
                self.edit_logradouro.setText(e.get("logradouro", ""))
                self.edit_cidade.setText(e.get("cidade", ""))
                self.edit_estado.setText(e.get("estado", ""))
                self.edit_pais.setText(e.get("pais", "Brasil"))

                self.edit_diagnostico.setText(c.get("diagnostico", ""))
                self.edit_historia_medica.setPlainText(c.get("historia_medica", ""))
                self.edit_alergias.setText(c.get("alergias", ""))
                self.edit_medicacoes.setText(c.get("medicacoes", ""))
                self.edit_habitos.setText(c.get("habitos", ""))
                self.edit_planejamento.setPlainText(c.get("planejamento", ""))

                self.edit_fotos.setText(paths.get("fotos", ""))
                self.edit_tomografia.setText(paths.get("dicom", ""))
                self.edit_maxila.setText(paths.get("maxila", ""))
                self.edit_mandibula.setText(paths.get("mandibula", ""))
                self.edit_face.setText(paths.get("face", ""))
            except Exception as ex:
                print(f"Erro ao carregar: {ex}")

    def _processar_cadastro(self):
        nome = self.edit_nome.text().strip()
        if not nome:
            QtWidgets.QMessageBox.warning(self.main_container, "Erro", "Nome é obrigatório.")
            return

        try:
            if self.pasta_paciente and Path(self.pasta_paciente).exists():
                diretorio = Path(self.pasta_paciente)
            else:
                diretorio = PASTA_PACIENTES / f"PRJ_{int(time.time())}_{nome.replace(' ', '_').upper()}"

            for sub in ["projeto", "modulo_tomografia", "modulo_osteotomia"]:
                (diretorio / sub).mkdir(parents=True, exist_ok=True)

            dados = {
                "paciente": {
                    "nome": nome, "cpf": self.edit_cpf.text(), "email": self.edit_email.text(),
                    "celular": self.edit_celular.text(), "estrangeiro": self.check_estrangeiro.isChecked(),
                    "nascimento": self.edit_nascimento.date().toString("yyyy-MM-dd"),
                    "sexo": self.combo_sexo.currentText()
                },
                "endereco": {
                    "cep": self.edit_cep.text(), "logradouro": self.edit_logradouro.text(),
                    "cidade": self.edit_cidade.text(), "estado": self.edit_estado.text(), "pais": self.edit_pais.text()
                },
                "clinico": {
                    "diagnostico": self.edit_diagnostico.text(),
                    "historia_medica": self.edit_historia_medica.toPlainText(),
                    "alergias": self.edit_alergias.text(), "medicacoes": self.edit_medicacoes.text(),
                    "habitos": self.edit_habitos.text(), "planejamento": self.edit_planejamento.toPlainText()
                },
                "caminhos": {
                    "workspace": str(diretorio.absolute()), "fotos": self.edit_fotos.text(),
                    "dicom": self.edit_tomografia.text(), "maxila": self.edit_maxila.text(),
                    "mandibula": self.edit_mandibula.text(), "face": self.edit_face.text()
                }
            }

            with open(diretorio / "projeto" / "info.json", "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)

            self.pasta_paciente = str(diretorio)
            QtWidgets.QMessageBox.information(self.main_container, "Sucesso", "Dados salvos!")
            self.concluido.emit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_container, "Erro", str(e))

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.main_container.layout(): return self.main_container
        layout = QtWidgets.QVBoxLayout(self.main_container)

        # 1. Informações Paciente
        gp = QtWidgets.QGroupBox("Informações do Paciente");
        lp = QtWidgets.QVBoxLayout(gp)
        r1 = QtWidgets.QHBoxLayout();
        r1.addWidget(QtWidgets.QLabel("Nome:"));
        r1.addWidget(self.edit_nome);
        r1.addWidget(self.check_estrangeiro)
        r2 = QtWidgets.QHBoxLayout();
        r2.addWidget(QtWidgets.QLabel("CPF:"));
        r2.addWidget(self.edit_cpf);
        r2.addWidget(QtWidgets.QLabel("Celular:"));
        r2.addWidget(self.edit_celular)
        r3 = QtWidgets.QHBoxLayout();
        r3.addWidget(QtWidgets.QLabel("E-mail:"));
        r3.addWidget(self.edit_email);
        r3.addWidget(QtWidgets.QLabel("Nasc.:"));
        r3.addWidget(self.edit_nascimento);
        r3.addWidget(QtWidgets.QLabel("Sexo:"));
        r3.addWidget(self.combo_sexo)
        lp.addLayout(r1);
        lp.addLayout(r2);
        lp.addLayout(r3);
        layout.addWidget(gp)

        # 2. Endereço
        sec_end = SecaoRetratil("Endereço", False);
        f_end = QtWidgets.QFormLayout()
        row_cep = QtWidgets.QHBoxLayout();
        row_cep.addWidget(self.edit_cep);
        row_cep.addWidget(self.btn_buscar_cep)
        f_end.addRow("CEP:", row_cep);
        f_end.addRow("Logradouro:", self.edit_logradouro);
        f_end.addRow("Cidade:", self.edit_cidade);
        f_end.addRow("Estado:", self.edit_estado);
        f_end.addRow("País:", self.edit_pais)
        sec_end.layout_interno().addLayout(f_end);
        layout.addWidget(sec_end)

        # 3. Dados Clínicos
        sec_clin = SecaoRetratil("Dados clínicos", False);
        f_clin = QtWidgets.QFormLayout()
        f_clin.addRow("Diagnóstico:", self.edit_diagnostico);
        f_clin.addRow("História Médica:", self.edit_historia_medica)
        f_clin.addRow("Alergias:", self.edit_alergias);
        f_clin.addRow("Medicações:", self.edit_medicacoes)
        f_clin.addRow("Hábitos/Vícios:", self.edit_habitos);
        f_clin.addRow("Planejamento:", self.edit_planejamento)
        sec_clin.layout_interno().addLayout(f_clin);
        layout.addWidget(sec_clin)

        # 4. Arquivos Base (Visível por padrão)
        sec_arq = SecaoRetratil("Arquivos do paciente", True);
        f_arq = QtWidgets.QFormLayout()
        f_arq.addRow("Tomografia:", self._criar_linha_arquivo(self.edit_tomografia, True))
        f_arq.addRow("Scan Maxila:", self._criar_linha_arquivo(self.edit_maxila, False))
        f_arq.addRow("Scan Mandíbula:", self._criar_linha_arquivo(self.edit_mandibula, False))
        f_arq.addRow("Scan Face:", self._criar_linha_arquivo(self.edit_face, False))
        f_arq.addRow("Fotografias:", self._criar_linha_arquivo(self.edit_fotos, True))
        sec_arq.layout_interno().addLayout(f_arq);
        layout.addWidget(sec_arq)

        self.btn_salvar.setMinimumHeight(40);
        self.btn_salvar.clicked.connect(self._processar_cadastro)
        layout.addStretch();
        layout.addWidget(self.btn_salvar)
        return self.main_container

    def _criar_linha_arquivo(self, edit, folder=True):
        w = QtWidgets.QWidget();
        l = QtWidgets.QHBoxLayout(w);
        l.setContentsMargins(0, 0, 0, 0);
        l.addWidget(edit)
        b = QtWidgets.QToolButton();
        b.setText("...");
        b.clicked.connect(lambda: self._buscar_caminho(edit, folder));
        l.addWidget(b)
        return w

    def _buscar_caminho(self, target, folder=True):
        p = QtWidgets.QFileDialog.getExistingDirectory(self.main_container, "Selecionar Pasta") if folder else \
            QtWidgets.QFileDialog.getOpenFileName(self.main_container, "Selecionar Arquivo", "",
                                                  "Malhas (*.stl *.obj *.ply)")[0]
        if p: target.setText(p)

    def get_toolbox(self) -> QtWidgets.QWidget:
        toolbox = QtWidgets.QWidget();
        lay = QtWidgets.QVBoxLayout(toolbox)
        btn = QtWidgets.QPushButton(" Limpar Formulário")
        btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogDiscardButton))
        btn.setStyleSheet(
            "background-color: #e74c3c; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        btn.clicked.connect(lambda: self._limpar_formulario())
        lay.addWidget(btn);
        lay.addStretch()
        return toolbox