from pathlib import Path
import time
import logging
from PySide6 import QtWidgets, QtCore

from modules.mod_patients.ui_components import SecaoRetratil, criar_linha_arquivo
from modules.mod_patients.logic import buscar_cep_online, formatar_nome_diretorio


class PersonalDataTab(QtWidgets.QWidget):
    concluido = QtCore.Signal()

    def __init__(self, project_manager):
        super().__init__()

        self.project_manager = project_manager
        self.pasta_paciente = None

        self._init_ui()
        self._setup_maps()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)

        content = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(content)

        # --- paciente ---
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

        gp = QtWidgets.QGroupBox("Informações do Paciente")
        lp = QtWidgets.QVBoxLayout(gp)

        r1 = QtWidgets.QHBoxLayout()
        r1.addWidget(QtWidgets.QLabel("Nome:"))
        r1.addWidget(self.edit_nome)
        r1.addWidget(self.check_estrangeiro)

        r2 = QtWidgets.QHBoxLayout()
        r2.addWidget(QtWidgets.QLabel("CPF:"))
        r2.addWidget(self.edit_cpf)
        r2.addWidget(QtWidgets.QLabel("Celular:"))
        r2.addWidget(self.edit_celular)

        r3 = QtWidgets.QHBoxLayout()
        r3.addWidget(QtWidgets.QLabel("E-mail:"))
        r3.addWidget(self.edit_email)
        r3.addWidget(QtWidgets.QLabel("Nasc.:"))
        r3.addWidget(self.edit_nascimento)
        r3.addWidget(QtWidgets.QLabel("Sexo:"))
        r3.addWidget(self.combo_sexo)

        for r in (r1, r2, r3):
            lp.addLayout(r)

        lay.addWidget(gp)

        # --- endereço ---
        self.edit_cep = QtWidgets.QLineEdit()
        self.edit_cep.setInputMask("00000-000;_")

        self.btn_buscar_cep = QtWidgets.QPushButton("Buscar")
        self.btn_buscar_cep.clicked.connect(self._buscar_cep)

        self.edit_logradouro = QtWidgets.QLineEdit()
        self.edit_cidade = QtWidgets.QLineEdit()
        self.edit_estado = QtWidgets.QLineEdit()
        self.edit_pais = QtWidgets.QLineEdit()
        self.edit_pais.setText("Brasil")

        sec_end = SecaoRetratil("Endereço", False)
        f_end = QtWidgets.QFormLayout()

        row_cep = QtWidgets.QHBoxLayout()
        row_cep.addWidget(self.edit_cep)
        row_cep.addWidget(self.btn_buscar_cep)

        f_end.addRow("CEP:", row_cep)
        f_end.addRow("Logradouro:", self.edit_logradouro)
        f_end.addRow("Cidade:", self.edit_cidade)
        f_end.addRow("Estado:", self.edit_estado)
        f_end.addRow("País:", self.edit_pais)

        sec_end.layout_interno().addLayout(f_end)
        lay.addWidget(sec_end)

        # --- clínico ---
        self.edit_diagnostico = QtWidgets.QLineEdit()
        self.edit_historia_medica = QtWidgets.QTextEdit()
        self.edit_historia_medica.setMaximumHeight(60)

        self.edit_alergias = QtWidgets.QLineEdit()
        self.edit_medicacoes = QtWidgets.QLineEdit()
        self.edit_habitos = QtWidgets.QLineEdit()

        self.edit_planejamento = QtWidgets.QTextEdit()
        self.edit_planejamento.setMaximumHeight(80)

        sec_clin = SecaoRetratil("Dados clínicos", False)
        f_clin = QtWidgets.QFormLayout()

        f_clin.addRow("Diagnóstico:", self.edit_diagnostico)
        f_clin.addRow("História Médica:", self.edit_historia_medica)
        f_clin.addRow("Alergias:", self.edit_alergias)
        f_clin.addRow("Medicações:", self.edit_medicacoes)
        f_clin.addRow("Hábitos/Vícios:", self.edit_habitos)
        f_clin.addRow("Planejamento:", self.edit_planejamento)

        sec_clin.layout_interno().addLayout(f_clin)
        lay.addWidget(sec_clin)

        lay.addStretch()

        self.btn_salvar = QtWidgets.QPushButton("Salvar Projeto")
        self.btn_salvar.setMinimumHeight(45)
        self.btn_salvar.clicked.connect(self._salvar)

        lay.addWidget(self.btn_salvar)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _setup_maps(self):
        self.map_paciente = {
            "nome": self.edit_nome,
            "cpf": self.edit_cpf,
            "email": self.edit_email,
            "celular": self.edit_celular,
            "sexo": self.combo_sexo
        }

        self.map_endereco = {
            "cep": self.edit_cep,
            "logradouro": self.edit_logradouro,
            "cidade": self.edit_cidade,
            "estado": self.edit_estado,
            "pais": self.edit_pais
        }

        self.map_clinico = {
            "diagnostico": self.edit_diagnostico,
            "historia_medica": self.edit_historia_medica,
            "alergias": self.edit_alergias,
            "medicacoes": self.edit_medicacoes,
            "habitos": self.edit_habitos,
            "planejamento": self.edit_planejamento
        }

    def _toggle_estrangeiro(self, state):
        is_estrangeiro = state == QtCore.Qt.Checked
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
        dados = buscar_cep_online(self.edit_cep.text())
        if not dados:
            return

        self.edit_logradouro.setText(dados.get("logradouro", ""))
        self.edit_cidade.setText(dados.get("cidade", ""))
        self.edit_estado.setText(dados.get("estado", ""))
        self.edit_pais.setText(dados.get("pais", "Brasil"))

    def carregar(self, pasta: str):
        self.pasta_paciente = pasta
        data = self.project_manager.loading_project(Path(pasta))
        if not data:
            return

        try:
            for sec, mapping in {
                "paciente": self.map_paciente,
                "endereco": self.map_endereco,
                "clinico": self.map_clinico
            }.items():
                for k, w in mapping.items():
                    val = data.get(sec, {}).get(k, "")
                    if isinstance(w, QtWidgets.QLineEdit):
                        w.setText(val)
                    elif isinstance(w, QtWidgets.QTextEdit):
                        w.setPlainText(val)
                    elif isinstance(w, QtWidgets.QComboBox):
                        w.setCurrentText(val)

            p = data.get("paciente", {})
            self.check_estrangeiro.setChecked(p.get("estrangeiro", False))

            if p.get("nascimento"):
                self.edit_nascimento.setDate(
                    QtCore.QDate.fromString(p["nascimento"], "yyyy-MM-dd")
                )

        except Exception as e:
            logging.error(e)

    def _salvar(self):
        if self.project_manager is None:
            QtWidgets.QMessageBox.critical(self, "Erro", "ProjectManager não inicializado.")
            return

        nome = self.edit_nome.text().strip()
        if not nome:
            QtWidgets.QMessageBox.warning(self, "Erro", "Nome é obrigatório.")
            return

        base = Path(self.pasta_paciente) if self.pasta_paciente else None

        if base is None or not base.exists():
            base = Path("patients") / formatar_nome_diretorio(nome, time.time())

        base = base.resolve()

        self.project_manager.inicializar_estrutura_paciente(base)
        self.pasta_paciente = str(base)

        def val(w):
            if isinstance(w, QtWidgets.QLineEdit):
                return w.text()
            if isinstance(w, QtWidgets.QTextEdit):
                return w.toPlainText()
            if isinstance(w, QtWidgets.QComboBox):
                return w.currentText()
            return ""

        dados = {
            "paciente": {k: val(v) for k, v in self.map_paciente.items()},
            "endereco": {k: val(v) for k, v in self.map_endereco.items()},
            "clinico": {k: val(v) for k, v in self.map_clinico.items()}
        }

        dados["paciente"]["estrangeiro"] = self.check_estrangeiro.isChecked()
        dados["paciente"]["nascimento"] = self.edit_nascimento.date().toString("yyyy-MM-dd")

        try:
            ok = self.project_manager.save_project(base, dados)

            if ok is False:
                QtWidgets.QMessageBox.critical(self, "Erro", "Falha ao salvar projeto.")
                return

            QtWidgets.QMessageBox.information(self, "Sucesso", f"Projeto salvo:\n{base}")
            self.concluido.emit()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro ao salvar", str(e))