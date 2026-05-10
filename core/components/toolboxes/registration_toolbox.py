from PySide6 import QtWidgets, QtCore, QtGui


class Component(QtWidgets.QWidget):
    toolbox_name = "Alinhar Objetos"

    solicitarAlinhamento = QtCore.Signal()
    limparPontos = QtCore.Signal()
    targetChanged = QtCore.Signal(str)
    sourceChanged = QtCore.Signal(str)

    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo
        self._is_initializing = True  # Flag para evitar emissões durante inicialização
        self.setup_ui()
        self._is_initializing = False

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        group_sel = QtWidgets.QGroupBox("Seleção de Malhas")
        layout_sel = QtWidgets.QFormLayout(group_sel)

        self.combo_target = QtWidgets.QComboBox()
        self.combo_source = QtWidgets.QComboBox()
        self.combo_target.currentTextChanged.connect(self._on_target_changed)
        self.combo_source.currentTextChanged.connect(self._on_source_changed)

        layout_sel.addRow("Referência (Fix):", self.combo_target)
        layout_sel.addRow("Móvel (Source):", self.combo_source)
        layout.addWidget(group_sel)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Ponto", "Vista A (mm)", "Vista B (mm)"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(QtWidgets.QLabel("Correspondência de Pontos:"))
        layout.addWidget(self.table)

        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_clear = QtWidgets.QPushButton("Limpar Pontos")
        self.btn_align = QtWidgets.QPushButton("Alinhar objetos")
        self.btn_clear.clicked.connect(self.limparPontos.emit)
        self.btn_align.clicked.connect(self.solicitarAlinhamento.emit)

        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_align)
        layout.addLayout(btn_layout)

        self._validar_selecao()

    def _on_target_changed(self, texto):
        if not self._is_initializing:
            self._validar_selecao()
            self.targetChanged.emit(texto)

    def _on_source_changed(self, texto):
        if not self._is_initializing:
            self._validar_selecao()
            self.sourceChanged.emit(texto)

    def _validar_selecao(self):
        target = self.combo_target.currentText()
        source = self.combo_source.currentText()
        ready = target != "" and source != "" and target != source
        self.btn_align.setEnabled(ready)
        if target == source and target != "":
            self.btn_align.setToolTip("O objeto de referência e o móvel devem ser diferentes.")
        else:
            self.btn_align.setToolTip("")

    def atualizar_combos(self, lista_objetos):
        current_t = self.combo_target.currentText()
        current_s = self.combo_source.currentText()

        self.combo_target.blockSignals(True)
        self.combo_source.blockSignals(True)

        self.combo_target.clear()
        self.combo_source.clear()
        self.combo_target.addItem("")
        self.combo_source.addItem("")
        self.combo_target.addItems(lista_objetos)
        self.combo_source.addItems(lista_objetos)

        if current_t in lista_objetos:
            self.combo_target.setCurrentText(current_t)
        if current_s in lista_objetos:
            self.combo_source.setCurrentText(current_s)

        self.combo_target.blockSignals(False)
        self.combo_source.blockSignals(False)
        # Não chamar _validar_selecao() aqui para evitar emissões desnecessárias

    def adicionar_ponto_tabela(self, vista, pos):
        pos_str = f"{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}"

        if vista == "A":
            row = self.table.rowCount()
            self.table.insertRow(row)
            item_id = QtWidgets.QTableWidgetItem(f"P {row + 1}")
            item_id.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 0, item_id)
            item_pos = QtWidgets.QTableWidgetItem(pos_str)
            item_pos.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 1, item_pos)
        else:
            found = False
            for r in range(self.table.rowCount()):
                item_b = self.table.item(r, 2)
                if item_b is None or item_b.text() == "":
                    item_pos = QtWidgets.QTableWidgetItem(pos_str)
                    item_pos.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table.setItem(r, 2, item_pos)
                    found = True
                    break

            if not found:
                row = self.table.rowCount()
                self.table.insertRow(row)
                item_id = QtWidgets.QTableWidgetItem(f"P {row + 1}")
                item_id.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row, 0, item_id)
                item_pos = QtWidgets.QTableWidgetItem(pos_str)
                item_pos.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row, 2, item_pos)

        self.table.scrollToBottom()

    def get_target_name(self):
        return self.combo_target.currentText()

    def get_source_name(self):
        return self.combo_source.currentText()

    def limpar_tabela(self):
        self.table.setRowCount(0)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = QtWidgets.QMainWindow()
    window.resize(400, 600)
    widget = Component()
    widget.atualizar_combos(["Mandíbula", "Crânio", "Guia", "Scan Intraoral"])
    window.setCentralWidget(widget)
    window.show()
    sys.exit(app.exec())