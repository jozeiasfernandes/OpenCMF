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

        # Criamos o container IMEDIATAMENTE para ser o porto seguro dos widgets
        self.main_container = QtWidgets.QWidget()
        self._init_ui_components()

    def _init_ui_components(self):
        """Inicializa os widgets vinculando-os ao container principal."""
        # Note que passamos self.main_container como parent
        self.edit_nome = QtWidgets.QLineEdit(self.main_container)
        self.edit_nome.setPlaceholderText("Nome completo do paciente...")
        self.edit_nome.setMinimumHeight(28)

        self.edit_nascimento = QtWidgets.QDateEdit(self.main_container)
        self.edit_nascimento.setCalendarPopup(True)
        self.edit_nascimento.setDisplayFormat("dd/MM/yyyy")
        self.edit_nascimento.setDate(QtCore.QDate.currentDate().addYears(-30))

        self.combo_sexo = QtWidgets.QComboBox(self.main_container)
        self.combo_sexo.addItems(["Masculino", "Feminino", "Outro"])

        self.edit_raiz = QtWidgets.QLineEdit(self.main_container)
        self.edit_dicom = QtWidgets.QLineEdit(self.main_container)
        self.edit_maxila = QtWidgets.QLineEdit(self.main_container)
        self.edit_mandibula = QtWidgets.QLineEdit(self.main_container)
        self.edit_face = QtWidgets.QLineEdit(self.main_container)

        self.btn_salvar = QtWidgets.QPushButton("Salvar projeto", self.main_container)

    def _criar_linha_arquivo(self, line_edit, folder=True):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Garante que o line_edit ocupe o espaço e o botão fique fixo
        line_edit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(line_edit)

        btn_buscar = QtWidgets.QToolButton()
        btn_buscar.setText("...")
        btn_buscar.clicked.connect(lambda: self._buscar_caminho(line_edit, folder))
        layout.addWidget(btn_buscar)
        return container

    def _buscar_caminho(self, target_edit, folder=True):
        """Usa o main_container como pai para evitar janelas soltas."""
        if folder:
            path = QtWidgets.QFileDialog.getExistingDirectory(
                self.main_container, "Selecionar Pasta"
            )
        else:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.main_container, "Selecionar Arquivo", "", "Malhas (*.stl *.obj *.ply)"
            )
        if path:
            target_edit.setText(path)

    def get_workspace(self) -> QtWidgets.QWidget:
        # Se o layout já foi montado, apenas retorna o container
        if self.main_container.layout():
            return self.main_container

        layout = QtWidgets.QVBoxLayout(self.main_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Grupo Pessoal
        group_pessoal = QtWidgets.QGroupBox("Informações do Paciente")
        form_pessoal = QtWidgets.QFormLayout(group_pessoal)
        form_pessoal.setSpacing(10)
        form_pessoal.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self.edit_nome.setMinimumWidth(300)
        form_pessoal.addRow("Nome:", self.edit_nome)

        detalhes = QtWidgets.QHBoxLayout()
        self.edit_nascimento.setMinimumWidth(120)
        detalhes.addWidget(self.edit_nascimento)
        detalhes.addWidget(QtWidgets.QLabel(" Sexo: "))
        detalhes.addWidget(self.combo_sexo)
        detalhes.addStretch()
        form_pessoal.addRow("Nascimento:", detalhes)

        # Grupo Arquivos
        group_arquivos = QtWidgets.QGroupBox("Arquivos Base e Workspace")
        form_arquivos = QtWidgets.QFormLayout(group_arquivos)

        for edit in [self.edit_raiz, self.edit_dicom, self.edit_maxila, self.edit_mandibula, self.edit_face]:
            edit.setMinimumWidth(300)

        form_arquivos.addRow("Pasta Workspace:", self._criar_linha_arquivo(self.edit_raiz, True))
        form_arquivos.addRow("Pasta DICOM:", self._criar_linha_arquivo(self.edit_dicom, True))
        form_arquivos.addRow("STL Maxila:", self._criar_linha_arquivo(self.edit_maxila, False))
        form_arquivos.addRow("STL Mandíbula:", self._criar_linha_arquivo(self.edit_mandibula, False))
        form_arquivos.addRow("STL Face:", self._criar_linha_arquivo(self.edit_face, False))

        self.btn_salvar.setMinimumHeight(50)
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                font-weight: bold; font-size: 14px; 
                background-color: #34495e; color: white;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2c3e50; }
        """)

        # Conexão segura
        try:
            self.btn_salvar.clicked.disconnect()
        except:
            pass
        self.btn_salvar.clicked.connect(self._processar_cadastro)

        layout.addWidget(group_pessoal)
        layout.addWidget(group_arquivos)
        layout.addStretch()
        layout.addWidget(self.btn_salvar)

        return self.main_container

    def get_toolbox(self):
        return QtWidgets.QWidget()

    def _processar_cadastro(self):
        nome = self.edit_nome.text().strip()
        raiz = self.edit_raiz.text().strip()

        # Usamos self.main_container como pai das mensagens de aviso
        if not nome or not raiz:
            QtWidgets.QMessageBox.warning(self.main_container, "Atenção", "Preencha o Nome e a Pasta Workspace.")
            return

        try:
            timestamp = int(time.time())
            slug = nome.replace(" ", "_").upper()
            projeto_id = f"PRJ_{timestamp}_{slug}"
            diretorio = PASTA_PACIENTES / projeto_id

            for sub in ["projeto", "modulo_tomografia", "modulo_osteotomia", "modulo_guia"]:
                (diretorio / sub).mkdir(parents=True, exist_ok=True)

            dados = {
                "id": projeto_id,
                "paciente": {"nome": nome, "sexo": self.combo_sexo.currentText()},
                "caminhos": {"workspace": str(Path(raiz) / slug), "dicom": self.edit_dicom.text()}
            }

            info_path = diretorio / "projeto" / "info.json"
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)

            self.pasta_paciente = str(diretorio)
            QtWidgets.QMessageBox.information(self.main_container, "Sucesso", "Paciente cadastrado!")

            # Avisa a MainWindow que este módulo terminou
            self.concluido.emit()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_container, "Erro", f"Falha ao salvar: {str(e)}")