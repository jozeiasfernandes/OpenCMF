import time
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from PySide6 import QtWidgets, QtCore


from project_manager.project_service import ProjectServiceHomePage

from application.patient.patient_manager import PatientManager

from project_manager.new_project.new_project_ui import SecaoRetratil, criar_linha_arquivo
from project_manager.new_project import buscar_cep_online, formatar_nome_diretorio

# Workspace
from core.workspace.modules.base.base_module import ModuleBase

from core.settings.paths.list_paths import PATIENTS_DIR


class Modulo(ModuleBase):
    def __init__(self, context=None):
        super().__init__(context=context)
        self.nome = "Pacientes"
        self.id = "modulo.paciente"

        # Inicializa o serviço de projetos
        self.project_service = ProjectServiceHomePage(PATIENTS_DIR)

        # Obtém a instância singleton do PatientManager injetando o project_service
        self.patient_manager = PatientManager.get_instance(self.project_service)

        self._init_ui_components()
        self._setup_data_maps()
        self._construir_interface()

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

    def inicializar(self, path_pacient: str) -> None:
        """Inicializa o módulo recebendo o path do paciente e atualizando o PatientManager."""
        super().inicializar(path_pacient)

        if path_pacient:
            # Notifica o PatientManager central sobre o paciente ativo
            self.patient_manager.set_active_patient(path_pacient)

        data = self.patient_manager.data
        if not data:
            return

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
            logging.error(f"Erro ao carregar dados do paciente: {ex}")

    def _processar_cadastro(self):
        nome = self.edit_nome.text().strip()
        if not nome:
            QtWidgets.QMessageBox.warning(self, "Erro", "Nome obrigatório.")
            return

        try:
            current_path = self.patient_manager.current_path
            diretorio = Path(current_path) if current_path else PATIENTS_DIR / formatar_nome_diretorio(nome,
                                                                                                       time.time())

            # Inicializa a estrutura de pastas no disco se for novo projeto
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

            # Salva no disco via serviço
            self.project_service.save_project(diretorio, dados)

            # Atualiza o estado global no PatientManager (isso dispara os sinais reativos para o resto do app)
            self.patient_manager.set_active_patient(str(diretorio))

            QtWidgets.QMessageBox.information(self, "Sucesso", "Projeto salvo!")
            self.concluido.emit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", str(e))

    def _construir_interface(self):
        main_layout = self.layout()
        if not main_layout:
            main_layout = QtWidgets.QVBoxLayout(self)
            self.setLayout(main_layout)

        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        content = QtWidgets.QWidget()
        lay_content = QtWidgets.QVBoxLayout(content)

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
        for r in [r1, r2, r3]: lp.addLayout(r)
        lay_content.addWidget(gp)

        sec_end = SecaoRetratil("Endereço", False, content)
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
        lay_content.addWidget(sec_end)

        sec_clin = SecaoRetratil("Dados clínicos", False, content)
        f_clin = QtWidgets.QFormLayout()
        f_clin.addRow("Diagnóstico:", self.edit_diagnostico)
        f_clin.addRow("História Médica:", self.edit_historia_medica)
        f_clin.addRow("Alergias:", self.edit_alergias)
        f_clin.addRow("Medicações:", self.edit_medicacoes)
        f_clin.addRow("Hábitos/Vícios:", self.edit_habitos)
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
        self.btn_salvar.clicked.connect(self._processar_cadastro)
        lay_content.addWidget(self.btn_salvar)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def get_workspace(self) -> QtWidgets.QWidget:
        return self

    def get_central_area(self) -> QtWidgets.QWidget:
        return self

    def get_workspace_toolbar(self, tool_manager: Any = None) -> Optional[QtWidgets.QToolBar]:
        return None

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        return {}

    def cleanup(self) -> None:
        logging.info(f"Limpando recursos do módulo: {self.id}")

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
            for w in self.findChildren(QtWidgets.QLineEdit): w.clear()
            for w in self.findChildren(QtWidgets.QTextEdit): w.clear()
            self.edit_pais.setText("Brasil")
            self.check_estrangeiro.setChecked(False)
            self.edit_nascimento.setDate(QtCore.QDate.currentDate())