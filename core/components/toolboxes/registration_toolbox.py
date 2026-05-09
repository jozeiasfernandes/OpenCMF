from PySide6 import QtWidgets, QtCore


class Component(QtWidgets.QWidget):
    toolbox_name = "Alinhar Objetos"
    solicitarAlinhamento = QtCore.Signal()
    limparPontos = QtCore.Signal()

    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo
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
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

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

    def adicionar_ponto_tabela(self, vista, pos):
        pos_str = f"{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}"

        if vista == "A":
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(f"Ponto {row + 1}"))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(pos_str))
        else:
            # Tenta encontrar a primeira linha onde a Vista B está vazia
            for r in range(self.table.rowCount()):
                item_b = self.table.item(r, 2)
                if item_b is None or item_b.text() == "":
                    self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(pos_str))
                    return

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(f"Ponto {row + 1}"))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(pos_str))

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


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("OpenCMF - Teste RegistrationWidget")
    window.resize(400, 600)

    widget = Component()

    objetos_teste = ["Mandíbula", "Crânio", "Guia Cirúrgico", "Dentição"]
    widget.atualizar_combos(objetos_teste)


    def simular_alinhamento():
        target = widget.get_target_name()
        source = widget.get_source_name()
        print(f"Solicitando alinhamento: {source} -> {target}")


    widget.solicitarAlinhamento.connect(simular_alinhamento)
    widget.limparPontos.connect(lambda: print("Pontos resetados"))

    # Simulação de adição de pontos via cliques nas vistas
    widget.adicionar_ponto_tabela("A", (10.5, 20.0, 5.2))
    widget.adicionar_ponto_tabela("B", (11.0, 19.8, 5.0))
    widget.adicionar_ponto_tabela("A", (50.1, -10.3, 0.0))

    window.setCentralWidget(widget)
    window.show()

    sys.exit(app.exec())