import time
import logging
from pathlib import Path
from typing import Dict
from PySide6 import QtWidgets, QtCore
from core.base_module.base import ModuloBase
from core.home_page.managers.project_service_home_page import ProjectServiceHomePage
from modules.mod_patients.ui_components import SecaoRetratil, criar_linha_arquivo
from modules.mod_patients.logic import buscar_cep_online, formatar_nome_diretorio

PASTA_PACIENTES = Path("patients")


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Pacientes"
        self.id = "modulo.paciente"
        self.pasta_paciente = None
        self.project_service = ProjectServiceHomePage(PASTA_PACIENTES)

        self.main_container = QtWidgets.QWidget(self)
        self.layout_modulo = QtWidgets.QVBoxLayout(self)
        self.layout_modulo.setContentsMargins(0, 0, 0, 0)
        self.layout_modulo.addWidget(self.main_container)

        self._init_ui_components()
        self._setup_data_maps()

    def _init_ui_components(self):
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

        self.edit_cep = QtWidgets.QLineEdit()
        self.edit_cep.setInputMask("00000-000;_")
        self.btn_buscar_cep = QtWidgets.QPushButton("Buscar")
        self.btn_buscar_cep.clicked.connect(self._buscar_cep)

        self.edit_logradouro = QtWidgets.QLineEdit()
        self.edit_cidade = QtWidgets.QLineEdit()
        self.edit_estado = QtWidgets.QLineEdit()
        self.edit_pais = QtWidgets.QLineEdit()
        self.edit_pais.setText("Brasil")

        self.edit_diagnostico = QtWidgets.QLineEdit()
        self.edit_historia_medica = QtWidgets.QTextEdit()
        self.edit_historia_medica.setMaximumHeight(60)
        self.edit_alergias = QtWidgets.QLineEdit()
        self.edit_medicacoes = QtWidgets.QLineEdit()
        self.edit_habitos = QtWidgets.QLineEdit()
        self.edit_planejamento = QtWidgets.QTextEdit()
        self.edit_planejamento.setMaximumHeight(80)

        self.edit_fotos = QtWidgets.QLineEdit()
        self.edit_tomografia = QtWidgets.QLineEdit()
        self.edit_maxila = QtWidgets.QLineEdit()
        self.edit_mandibula = QtWidgets.QLineEdit()
        self.edit_face = QtWidgets.QLineEdit()

        self.btn_salvar = QtWidgets.QPushButton("Salvar Projeto")

    def _setup_data_maps(self):
        self.map_paciente = {
            "nome": self.edit_nome, "cpf": self.edit_cpf, "email": self.edit_email,
            "celular": self.edit_celular, "sexo": self.combo_sexo
        }
        self.map_endereco = {
            "cep": self.edit_cep, "logradouro": self.edit_logradouro,
            "cidade": self.edit_cidade, "estado": self.edit_estado, "pais": self.edit_pais
        }
        self.map_clinico = {
            "diagnostico": self.edit_diagnostico, "historia_medica": self.edit_historia_medica,
            "alergias": self.edit_alergias, "medicacoes": self.edit_medicacoes,
            "habitos": self.edit_habitos, "planejamento": self.edit_planejamento
        }
        self.map_caminhos = {
            "fotos": self.edit_fotos, "dicom": self.edit_tomografia,
            "maxila": self.edit_maxila, "mandibula": self.edit_mandibula, "face": self.edit_face
        }

    def _toggle_estrangeiro(self, state):
        is_estrangeiro = (state == QtCore.Qt.Checked or state == 2)
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
        if dados:
            self.edit_logradouro.setText(dados.get("logradouro", ""))
            self.edit_cidade.setText(dados.get("cidade", ""))
            self.edit_estado.setText(dados.get("estado", ""))
            self.edit_pais.setText(dados.get("pais", "Brasil"))

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.pasta_paciente = caminho_paciente
        data = self.project_service.load_project(Path(caminho_paciente))
        if not data: return

        try:
            sections = {
                "paciente": self.map_paciente,
                "endereco": self.map_endereco,
                "clinico": self.map_clinico,
                "caminhos": self.map_caminhos
            }

            for sec_key, mapping in sections.items():
                sec_data = data.get(sec_key, {})
                for key, widget in mapping.items():
                    val = sec_data.get(key, "")
                    if isinstance(widget, QtWidgets.QLineEdit):
                        widget.setText(val)
                    elif isinstance(widget, QtWidgets.QTextEdit):
                        widget.setPlainText(val)
                    elif isinstance(widget, QtWidgets.QComboBox):
                        widget.setCurrentText(val)

            p_data = data.get("paciente", {})
            self.check_estrangeiro.setChecked(p_data.get("estrangeiro", False))
            if p_data.get("nascimento"):
                self.edit_nascimento.setDate(QtCore.QDate.fromString(p_data["nascimento"], "yyyy-MM-dd"))
        except Exception as ex:
            logging.error(f"Erro carregar: {ex}")

    def _processar_cadastro(self):
        nome = self.edit_nome.text().strip()
        if not nome:
            QtWidgets.QMessageBox.warning(self, "Erro", "Nome obrigatório.")
            return

        try:
            diretorio = Path(self.pasta_paciente) if self.pasta_paciente else PASTA_PACIENTES / formatar_nome_diretorio(
                nome, time.time())

            self.project_service.initialize_patient_structure(diretorio)

            get_val = lambda w: w.text() if isinstance(w, QtWidgets.QLineEdit) else (
                w.toPlainText() if isinstance(w, QtWidgets.QTextEdit) else w.currentText())

            dados_antigos = self.project_service.load_project(diretorio) or {}

            dados = {
                "paciente": {k: get_val(v) for k, v in self.map_paciente.items()},
                "endereco": {k: get_val(v) for k, v in self.map_endereco.items()},
                "clinico": {k: get_val(v) for k, v in self.map_clinico.items()},
                "caminhos": {k: get_val(v) for k, v in self.map_caminhos.items()},
                "objetos": dados_antigos.get("objetos", []),
                "created_at": dados_antigos.get("created_at", time.time())
            }
            dados["paciente"]["estrangeiro"] = self.check_estrangeiro.isChecked()
            dados["paciente"]["nascimento"] = self.edit_nascimento.date().toString("yyyy-MM-dd")

            self.project_service.save_project(diretorio, dados)
            self.pasta_paciente = str(diretorio)

            QtWidgets.QMessageBox.information(self, "Sucesso", "Projeto salvo!")
            self.concluido.emit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", str(e))

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.main_container.layout(): return self.main_container

        layout = QtWidgets.QVBoxLayout(self.main_container)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        content = QtWidgets.QWidget()
        lay_content = QtWidgets.QVBoxLayout(content)

        gp = QtWidgets.QGroupBox("Informações do Paciente")
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
        for r in [r1, r2, r3]: lp.addLayout(r)
        lay_content.addWidget(gp)

        sec_end = SecaoRetratil("Endereço", False, content)
        f_end = QtWidgets.QFormLayout()
        row_cep = QtWidgets.QHBoxLayout();
        row_cep.addWidget(self.edit_cep);
        row_cep.addWidget(self.btn_buscar_cep)
        f_end.addRow("CEP:", row_cep);
        f_end.addRow("Logradouro:", self.edit_logradouro);
        f_end.addRow("Cidade:", self.edit_cidade);
        f_end.addRow("Estado:", self.edit_estado);
        f_end.addRow("País:", self.edit_pais)
        sec_end.layout_interno().addLayout(f_end)
        lay_content.addWidget(sec_end)

        sec_clin = SecaoRetratil("Dados clínicos", False, content)
        f_clin = QtWidgets.QFormLayout()
        f_clin.addRow("Diagnóstico:", self.edit_diagnostico);
        f_clin.addRow("História Médica:", self.edit_historia_medica);
        f_clin.addRow("Alergias:", self.edit_alergias);
        f_clin.addRow("Medicações:", self.edit_medicacoes);
        f_clin.addRow("Hábitos/Vícios:", self.edit_habitos);
        f_clin.addRow("Planejamento:", self.edit_planejamento)
        sec_clin.layout_interno().addLayout(f_clin)
        lay_content.addWidget(sec_clin)

        sec_arq = SecaoRetratil("Arquivos do paciente", True, content)
        f_arq = QtWidgets.QFormLayout()
        f_arq.addRow("Tomografia:", criar_linha_arquivo(self.edit_tomografia, self._buscar_caminho, True))
        f_arq.addRow("Scan Maxila:", criar_linha_arquivo(self.edit_maxila, self._buscar_caminho, False))
        f_arq.addRow("Scan Mandíbula:", criar_linha_arquivo(self.edit_mandibula, self._buscar_caminho, False))
        f_arq.addRow("Scan Face:", criar_linha_arquivo(self.edit_face, self._buscar_caminho, False))
        f_arq.addRow("Fotografias:", criar_linha_arquivo(self.edit_fotos, self._buscar_caminho, True))
        sec_arq.layout_interno().addLayout(f_arq)
        lay_content.addWidget(sec_arq)

        lay_content.addStretch()
        self.btn_salvar.setMinimumHeight(45)
        self.btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_salvar.clicked.connect(self._processar_cadastro)
        lay_content.addWidget(self.btn_salvar)

        scroll.setWidget(content)
        layout.addWidget(scroll)
        return self.main_container

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        aba_acoes = QtWidgets.QWidget()
        lay_acoes = QtWidgets.QVBoxLayout(aba_acoes)
        btn_limpar = QtWidgets.QPushButton(" Limpar Formulário")
        btn_limpar.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogDiscardButton))
        btn_limpar.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 4px;")
        btn_limpar.clicked.connect(self._limpar_formulario)
        lay_acoes.addWidget(btn_limpar)
        lay_acoes.addStretch()
        return {"Ferramentas": aba_acoes}

    def _buscar_caminho(self, target, folder=True):
        settings = QtCore.QSettings("OpenCMF", "Config")
        chave = "ultimo_diretorio_dicom" if target == self.edit_tomografia else "ultimo_diretorio_geral"
        ultimo = settings.value(chave, "")
        p = QtWidgets.QFileDialog.getExistingDirectory(self, "Pasta", ultimo) if folder else \
        QtWidgets.QFileDialog.getOpenFileName(self, "Arquivo", ultimo, "Malhas (*.stl *.obj *.ply)")[0]
        if p:
            target.setText(p)
            settings.setValue(chave, p)

    def _limpar_formulario(self):
        if QtWidgets.QMessageBox.question(self, "Limpar", "Limpar tudo?") == QtWidgets.QMessageBox.Yes:
            for w in self.main_container.findChildren(QtWidgets.QLineEdit): w.clear()
            for w in self.main_container.findChildren(QtWidgets.QTextEdit): w.clear()
            self.edit_pais.setText("Brasil")
            self.check_estrangeiro.setChecked(False)
            self.edit_nascimento.setDate(QtCore.QDate.currentDate())