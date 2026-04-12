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

        # Container fixo para garantir que os dados apareçam na tela correta
        self.main_container = QtWidgets.QWidget()
        self._init_ui_components()

    def _init_ui_components(self):
        """Inicializa os widgets vinculando-os ao container principal."""
        self.edit_nome = QtWidgets.QLineEdit()
        self.edit_nome.setPlaceholderText("Nome completo do paciente...")
        self.edit_nome.setMinimumHeight(28)

        self.edit_nascimento = QtWidgets.QDateEdit()
        self.edit_nascimento.setCalendarPopup(True)
        self.edit_nascimento.setDisplayFormat("dd/MM/yyyy")
        self.edit_nascimento.setDate(QtCore.QDate.currentDate().addYears(-30))

        self.combo_sexo = QtWidgets.QComboBox()
        self.combo_sexo.addItems(["Masculino", "Feminino", "Outro"])

        self.edit_raiz = QtWidgets.QLineEdit()
        self.edit_dicom = QtWidgets.QLineEdit()
        self.edit_maxila = QtWidgets.QLineEdit()
        self.edit_mandibula = QtWidgets.QLineEdit()
        self.edit_face = QtWidgets.QLineEdit()

        self.btn_salvar = QtWidgets.QPushButton("Salvar / Atualizar Projeto")

    def inicializar(self, caminho_paciente: str) -> None:
        """
        CARREGAMENTO AUTOMÁTICO:
        Chamado pela MainWindow ao selecionar um paciente ou mudar de aba.
        """
        super().inicializar(caminho_paciente)
        self.pasta_paciente = caminho_paciente

        path_json = Path(caminho_paciente) / "projeto" / "info.json"

        if path_json.exists():
            try:
                with open(path_json, "r", encoding="utf-8") as f:
                    dados = json.load(f)

                # Preenche os campos da UI com os dados do JSON
                paciente = dados.get("paciente", {})
                caminhos = dados.get("caminhos", {})

                self.edit_nome.setText(paciente.get("nome", ""))
                self.combo_sexo.setCurrentText(paciente.get("sexo", "Masculino"))

                # Trata a data de nascimento
                data_nasc = paciente.get("nascimento")
                if data_nasc:
                    self.edit_nascimento.setDate(QtCore.QDate.fromString(data_nasc, "yyyy-MM-dd"))

                # Preenche caminhos
                self.edit_raiz.setText(caminhos.get("workspace", ""))
                self.edit_dicom.setText(caminhos.get("dicom", ""))
                self.edit_maxila.setText(caminhos.get("maxila", ""))
                self.edit_mandibula.setText(caminhos.get("mandibula", ""))
                self.edit_face.setText(caminhos.get("face", ""))

                print(f">>> [MODULO PACIENTE] Dados de {paciente.get('nome')} carregados com sucesso.")
            except Exception as e:
                print(f"Erro ao carregar dados do paciente: {e}")

    def _processar_cadastro(self):
        """SALVAR/ATUALIZAR: Salva sem excluir os dados antigos."""
        nome = self.edit_nome.text().strip()
        if not nome:
            QtWidgets.QMessageBox.warning(self.main_container, "Atenção", "O nome é obrigatório.")
            return

        try:
            # Se já temos um caminho (Paciente Maria carregado), usamos ele.
            # Se não, criamos uma nova pasta.
            if self.pasta_paciente and Path(self.pasta_paciente).exists():
                diretorio = Path(self.pasta_paciente)
                msg_sucesso = "Dados atualizados com sucesso!"
            else:
                timestamp = int(time.time())
                slug = nome.replace(" ", "_").upper()
                projeto_id = f"PRJ_{timestamp}_{slug}"
                diretorio = PASTA_PACIENTES / projeto_id
                msg_sucesso = "Novo paciente cadastrado!"

            # Garante a estrutura de pastas
            for sub in ["projeto", "modulo_tomografia", "modulo_osteotomia"]:
                (diretorio / sub).mkdir(parents=True, exist_ok=True)

            # Monta o dicionário (preservando o ID original se existir)
            info_path = diretorio / "projeto" / "info.json"

            # Carrega dados antigos para não perder referências de outros módulos
            dados_finais = {}
            if info_path.exists():
                with open(info_path, "r", encoding="utf-8") as f:
                    dados_finais = json.load(f)

            # Atualiza apenas o que mudou na interface
            dados_finais["paciente"] = {
                "nome": nome,
                "nascimento": self.edit_nascimento.date().toString("yyyy-MM-dd"),
                "sexo": self.combo_sexo.currentText()
            }

            # Garante que a chave caminhos exista antes de atualizar
            if "caminhos" not in dados_finais:
                dados_finais["caminhos"] = {}

            dados_finais["caminhos"].update({
                "workspace": self.edit_raiz.text(),
                "dicom": self.edit_dicom.text(),
                "maxila": self.edit_maxila.text(),
                "mandibula": self.edit_mandibula.text(),
                "face": self.edit_face.text()
            })

            # Salva o arquivo (Sobrescreve o antigo com a união dos dados)
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(dados_finais, f, indent=4, ensure_ascii=False)

            self.pasta_paciente = str(diretorio)
            QtWidgets.QMessageBox.information(self.main_container, "Sucesso", msg_sucesso)

            # Avisa a MainWindow para avançar ou atualizar lista
            self.concluido.emit()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_container, "Erro", f"Falha ao salvar: {str(e)}")

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.main_container.layout():
            return self.main_container

        layout = QtWidgets.QVBoxLayout(self.main_container)

        # Grupo Pessoal
        group_pessoal = QtWidgets.QGroupBox("Informações do Paciente")
        form_pessoal = QtWidgets.QFormLayout(group_pessoal)
        form_pessoal.addRow("Nome:", self.edit_nome)

        detalhes = QtWidgets.QHBoxLayout()
        detalhes.addWidget(self.edit_nascimento)
        detalhes.addWidget(QtWidgets.QLabel(" Sexo: "))
        detalhes.addWidget(self.combo_sexo)
        form_pessoal.addRow("Nascimento:", detalhes)

        # Grupo Arquivos
        group_arquivos = QtWidgets.QGroupBox("Arquivos Base e Workspace")
        form_arquivos = QtWidgets.QFormLayout(group_arquivos)
        form_arquivos.addRow("Pasta Workspace:", self._criar_linha_arquivo(self.edit_raiz, True))
        form_arquivos.addRow("Pasta DICOM:", self._criar_linha_arquivo(self.edit_dicom, True))
        form_arquivos.addRow("STL Maxila:", self._criar_linha_arquivo(self.edit_maxila, False))
        form_arquivos.addRow("STL Mandíbula:", self._criar_linha_arquivo(self.edit_mandibula, False))
        form_arquivos.addRow("STL Face:", self._criar_linha_arquivo(self.edit_face, False))

        # Estilo do Botão
        self.btn_salvar.setMinimumHeight(40)
        self.btn_salvar.clicked.connect(self._processar_cadastro)

        layout.addWidget(group_pessoal)
        layout.addWidget(group_arquivos)
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
            path = QtWidgets.QFileDialog.getExistingDirectory(self.main_container, "Selecionar Pasta")
        else:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self.main_container, "Selecionar Arquivo", "",
                                                            "Malhas (*.stl *.obj *.ply)")
        if path:
            target_edit.setText(path)

    def get_toolbox(self):
        return QtWidgets.QWidget()