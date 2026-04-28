from PySide6 import QtWidgets, QtCore


class RegistrationWidget(QtWidgets.QWidget):
    solicitarAlinhamento = QtCore.Signal()
    limparPontos = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        group_sel = QtWidgets.QGroupBox("Seleção de Objetos")
        layout_sel = QtWidgets.QFormLayout(group_sel)

        self.combo_target = QtWidgets.QComboBox()
        self.combo_source = QtWidgets.QComboBox()

        layout_sel.addRow("Referência (Fix):", self.combo_target)
        layout_sel.addRow("Móvel (Source):", self.combo_source)
        layout.addWidget(group_sel)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Ponto", "Vista A", "Vista B"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(QtWidgets.QLabel("Pontos Marcados:"))
        layout.addWidget(self.table)

        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_clear = QtWidgets.QPushButton("Limpar")
        self.btn_align = QtWidgets.QPushButton("Alinhar")
        self.btn_align.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")

        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_align)
        layout.addLayout(btn_layout)

        self.btn_clear.clicked.connect(self.limparPontos.emit)
        self.btn_align.clicked.connect(self.solicitarAlinhamento.emit)

    def get_target_name(self):
        return self.combo_target.currentText()

    def get_source_name(self):
        return self.combo_source.currentText()

    def atualizar_combos(self, lista_objetos):
        self.combo_target.clear()
        self.combo_source.clear()
        self.combo_target.addItems(lista_objetos)
        self.combo_source.addItems(lista_objetos)

    def limpar_tabela(self):
        self.table.setRowCount(0)