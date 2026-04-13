import json
import time
from pathlib import Path
from typing import Dict
from PySide6 import QtWidgets, QtCore, QtGui
from core.base import ModuloBase

from modulos.mod_Paciente.ui_components import SecaoRetratil, criar_linha_arquivo
from modulos.mod_Paciente.logic import buscar_cep_online, formatar_nome_diretorio

PASTA_PACIENTES = Path("pacientes")


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Cadastro de Paciente"
        self.id = "modulo.paciente"
        self.pasta_paciente = None
        PASTA_PACIENTES.mkdir(exist_ok=True)

        self.main_container = QtWidgets.QWidget()
        self._init_ui_components()
        self._setup_data_maps()

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
            self.edit_logradouro.setText(dados["logradouro"])
            self.edit_cidade.setText(dados["cidade"])
            self.edit_estado.setText(dados["estado"])
            self.edit_pais.setText(dados["pais"])

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.pasta_paciente = caminho_paciente
        path_json = Path(caminho_paciente) / "projeto" / "info.json"

        if not path_json.exists(): return

        try:
            with open(path_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            sections = {"paciente": self.map_paciente, "endereco": self.map_endereco,
                        "clinico": self.map_clinico, "caminhos": self.map_caminhos}

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
            print(f"Erro ao carregar: {ex}")

    def _processar_cadastro(self):
        nome = self.edit_nome.text().strip()
        if not nome:
            QtWidgets.QMessageBox.warning(self.main_container, "Erro", "Nome é obrigatório.")
            return

        try:
            diretorio = Path(self.pasta_paciente) if self.pasta_paciente else PASTA_PACIENTES / formatar_nome_diretorio(
                nome, time.time())
            for sub in ["projeto", "modulo_tomografia", "modulo_osteotomia"]:
                (diretorio / sub).mkdir(parents=True, exist_ok=True)

            get_val = lambda w: w.text() if isinstance(w, QtWidgets.QLineEdit) else (
                w.toPlainText() if isinstance(w, QtWidgets.QTextEdit) else w.currentText())

            dados = {
                "paciente": {k: get_val(v) for k, v in self.map_paciente.items()},
                "endereco": {k: get_val(v) for k, v in self.map_endereco.items()},
                "clinico": {k: get_val(v) for k, v in self.map_clinico.items()},
                "caminhos": {k: get_val(v) for k, v in self.map_caminhos.items()}
            }
            dados["paciente"]["estrangeiro"] = self.check_estrangeiro.isChecked()
            dados["paciente"]["nascimento"] = self.edit_nascimento.date().toString("yyyy-MM-dd")
            dados["caminhos"]["workspace"] = str(diretorio.absolute())

            with open(diretorio / "projeto" / "info.json", "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)

            self.pasta_paciente = str(diretorio)
            QtWidgets.QMessageBox.information(self.main_container, "Sucesso", "Dados salvos!")
            self.concluido.emit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_container, "Erro", str(e))

    def get_workspace(self) -> QtWidgets.QWidget:
        # Se já tiver layout, apenas retorna para evitar reconstrução
        if self.main_container.layout(): return self.main_container

        layout = QtWidgets.QVBoxLayout(self.main_container)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        content = QtWidgets.QWidget()
        lay_content = QtWidgets.QVBoxLayout(content)

        # 1. Informações Paciente
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

        # 2. Seções Retráteis
        sec_end = SecaoRetratil("Endereço", False)
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
        lay_content.addWidget(sec_end)

        sec_clin = SecaoRetratil("Dados clínicos", False)
        f_clin = QtWidgets.QFormLayout()
        f_clin.addRow("Diagnóstico:", self.edit_diagnostico);
        f_clin.addRow("História Médica:", self.edit_historia_medica);
        f_clin.addRow("Alergias:", self.edit_alergias);
        f_clin.addRow("Medicações:", self.edit_medicacoes);
        f_clin.addRow("Hábitos/Vícios:", self.edit_habitos);
        f_clin.addRow("Planejamento:", self.edit_planejamento)
        sec_clin.layout_interno().addLayout(f_clin);
        lay_content.addWidget(sec_clin)

        sec_arq = SecaoRetratil("Arquivos do paciente", True)
        f_arq = QtWidgets.QFormLayout()
        f_arq.addRow("Tomografia:", criar_linha_arquivo(self.edit_tomografia, self._buscar_caminho, True))
        f_arq.addRow("Scan Maxila:", criar_linha_arquivo(self.edit_maxila, self._buscar_caminho, False))
        f_arq.addRow("Scan Mandíbula:", criar_linha_arquivo(self.edit_mandibula, self._buscar_caminho, False))
        f_arq.addRow("Scan Face:", criar_linha_arquivo(self.edit_face, self._buscar_caminho, False))
        f_arq.addRow("Fotografias:", criar_linha_arquivo(self.edit_fotos, self._buscar_caminho, True))
        sec_arq.layout_interno().addLayout(f_arq);
        lay_content.addWidget(sec_arq)

        lay_content.addStretch()
        self.btn_salvar.setMinimumHeight(45)
        self.btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 14px;")
        self.btn_salvar.clicked.connect(self._processar_cadastro)
        lay_content.addWidget(self.btn_salvar)

        scroll.setWidget(content)
        layout.addWidget(scroll)
        return self.main_container

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        toolbar = QtWidgets.QToolBar("Ações do Paciente")
        action_save = toolbar.addAction("Salvar")
        action_save.triggered.connect(self._processar_cadastro)
        return toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """Adequação para a nova estrutura do WorkspaceManager (Multi-abas East)"""

        # Aba de Ações/Ferramentas
        aba_acoes = QtWidgets.QWidget()
        lay_acoes = QtWidgets.QVBoxLayout(aba_acoes)

        lbl = QtWidgets.QLabel("<b>Ações</b>")
        lay_acoes.addWidget(lbl)

        btn_limpar = QtWidgets.QPushButton(" Limpar Formulário")
        btn_limpar.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogDiscardButton))
        btn_limpar.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px; border-radius: 4px;")
        btn_limpar.clicked.connect(self._limpar_formulario)

        lay_acoes.addWidget(btn_limpar)
        lay_acoes.addStretch()

        return {
            "Ferramentas": aba_acoes
        }

    def _buscar_caminho(self, target, folder=True):
        if folder:
            p = QtWidgets.QFileDialog.getExistingDirectory(self.main_container, "Selecionar Pasta")
        else:
            p, _ = QtWidgets.QFileDialog.getOpenFileName(self.main_container, "Selecionar Arquivo", "",
                                                         "Malhas (*.stl *.obj *.ply)")
        if p: target.setText(p)

    def _limpar_formulario(self):
        confirm = QtWidgets.QMessageBox.question(self.main_container, "Limpar", "Deseja limpar todos os campos?")
        if confirm == QtWidgets.QMessageBox.Yes:
            for w in self.main_container.findChildren(QtWidgets.QLineEdit): w.clear()
            for w in self.main_container.findChildren(QtWidgets.QTextEdit): w.clear()
            self.edit_pais.setText("Brasil")
            self.check_estrangeiro.setChecked(False)
            self.edit_nascimento.setDate(QtCore.QDate.currentDate())