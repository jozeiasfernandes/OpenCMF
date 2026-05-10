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
        self._is_initializing = True
        self.setup_ui()
        self._is_initializing = False

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Deixa o ToolboxesManager controlar largura — sem mínimos fixos
        self.setMinimumSize(0, 0)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Preferred   # Preferred: não força expansão vertical
        )

        group_sel = QtWidgets.QGroupBox("Seleção de Malhas")
        layout_sel = QtWidgets.QFormLayout(group_sel)
        layout_sel.setContentsMargins(5, 5, 5, 5)
        layout_sel.setSpacing(6)

        self.combo_target = QtWidgets.QComboBox()
        self.combo_target.setMinimumWidth(0)
        self.combo_source = QtWidgets.QComboBox()
        self.combo_source.setMinimumWidth(0)
        self.combo_target.currentTextChanged.connect(self._on_target_changed)
        self.combo_source.currentTextChanged.connect(self._on_source_changed)
        layout_sel.addRow("Referência (Fix):", self.combo_target)
        layout_sel.addRow("Móvel (Source):", self.combo_source)
        layout.addWidget(group_sel)

        layout.addWidget(QtWidgets.QLabel("Correspondência de Pontos:"))

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Ponto", "Vista A", "Vista B"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumSize(0, 0)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.table.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Ignored     # Ignored: não contribui com nenhum mínimo
        )

        layout.addWidget(self.table, stretch=1)

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
        tip = "O objeto de referência e o móvel devem ser diferentes." if target == source and target != "" else ""
        self.btn_align.setToolTip(tip)

    def atualizar_combos(self, lista_objetos):
        current_t = self.combo_target.currentText()
        current_s = self.combo_source.currentText()
        self.combo_target.blockSignals(True)
        self.combo_source.blockSignals(True)
        self.combo_target.clear()
        self.combo_source.clear()
        for combo in [self.combo_target, self.combo_source]:
            combo.addItem("")
            combo.addItems(lista_objetos)
        if current_t in lista_objetos:
            self.combo_target.setCurrentText(current_t)
        if current_s in lista_objetos:
            self.combo_source.setCurrentText(current_s)
        self.combo_target.blockSignals(False)
        self.combo_source.blockSignals(False)
        self._validar_selecao()

    def adicionar_ponto_tabela(self, vista, pos):
        pos_str = f"{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}"
        if vista == "A":
            row = self.table.rowCount()
            self.table.insertRow(row)
            self._set_cell(row, 0, f"P {row + 1}")
            self._set_cell(row, 1, pos_str)
        else:
            found = False
            for r in range(self.table.rowCount()):
                item_b = self.table.item(r, 2)
                if item_b is None or item_b.text() == "":
                    self._set_cell(r, 2, pos_str)
                    found = True
                    break
            if not found:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self._set_cell(row, 0, f"P {row + 1}")
                self._set_cell(row, 2, pos_str)
        self.table.scrollToBottom()

    def _set_cell(self, row, col, text):
        item = QtWidgets.QTableWidgetItem(text)
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.table.setItem(row, col, item)

    def get_target_name(self):
        return self.combo_target.currentText()

    def get_source_name(self):
        return self.combo_source.currentText()

    def limpar_tabela(self):
        self.table.setRowCount(0)