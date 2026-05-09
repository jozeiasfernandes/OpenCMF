from PySide6 import QtWidgets, QtCore, QtGui


class Component(QtWidgets.QWidget):
    toolbox_name = "Alinhar Objetos"

    # Sinais de ação
    solicitarAlinhamento = QtCore.Signal()
    limparPontos = QtCore.Signal()

    # Sinais de sincronização com as janelas 3D
    targetChanged = QtCore.Signal(str)
    sourceChanged = QtCore.Signal(str)

    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        group_sel = QtWidgets.QGroupBox("Seleção de Malhas")
        layout_sel = QtWidgets.QFormLayout(group_sel)

        self.combo_target = QtWidgets.QComboBox()
        self.combo_source = QtWidgets.QComboBox()

        # Conexões de mudança com validação e emissão de sinal
        self.combo_target.currentTextChanged.connect(self._on_target_changed)
        self.combo_source.currentTextChanged.connect(self._on_source_changed)

        layout_sel.addRow("Referência (Fix):", self.combo_target)
        layout_sel.addRow("Móvel (Source):", self.combo_source)
        layout.addWidget(group_sel)

        # Configuração da Tabela
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Ponto", "Vista A (mm)", "Vista B (mm)"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        # Estilo para parecer mais profissional
        self.table.setStyleSheet("QTableWidget { gridline-color: #dcdde1; }")

        layout.addWidget(QtWidgets.QLabel("Correspondência de Pontos:"))
        layout.addWidget(self.table)

        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_clear = QtWidgets.QPushButton("Limpar Pontos")
        self.btn_align = QtWidgets.QPushButton("Executar Registro")
        self.btn_align.setFixedHeight(35)
        self.btn_align.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; 
                color: white; 
                font-weight: bold; 
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2ecc71; }
            QPushButton:pressed { background-color: #1e8449; }
            QPushButton:disabled { background-color: #7f8c8d; color: #ecf0f1; }
        """)

        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_align)
        layout.addLayout(btn_layout)

        self.btn_clear.clicked.connect(self.limparPontos.emit)
        self.btn_align.clicked.connect(self.solicitarAlinhamento.emit)

        self._validar_selecao()

    # --- LÓGICA DE INTERFACE E VALIDAÇÃO ---

    def _on_target_changed(self, texto):
        self._validar_selecao()
        self.targetChanged.emit(texto)

    def _on_source_changed(self, texto):
        self._validar_selecao()
        self.sourceChanged.emit(texto)

    def _validar_selecao(self):
        """Bloqueia o botão de alinhamento se os dados forem inválidos."""
        target = self.combo_target.currentText()
        source = self.combo_source.currentText()

        ready = (target != "" and source != "" and target != source)
        self.btn_align.setEnabled(ready)

        if target == source and target != "":
            self.btn_align.setToolTip("O objeto de referência e o móvel devem ser diferentes.")
        else:
            self.btn_align.setToolTip("")

    # --- MÉTODOS PÚBLICOS ---

    def atualizar_combos(self, lista_objetos):
        """Atualiza a lista sem perder a seleção atual se ela ainda existir."""
        current_t = self.combo_target.currentText()
        current_s = self.combo_source.currentText()

        self.combo_target.blockSignals(True)
        self.combo_source.blockSignals(True)

        self.combo_target.clear()
        self.combo_source.clear()

        # Adiciona opção vazia para não carregar nada por padrão
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
        self._validar_selecao()

    def adicionar_ponto_tabela(self, vista, pos):
        """Adiciona pontos à tabela garantindo o pareamento A/B."""
        pos_str = f"{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}"

        if vista == "A":
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Coluna ID
            item_id = QtWidgets.QTableWidgetItem(f"P {row + 1}")
            item_id.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 0, item_id)

            # Coluna Vista A
            item_pos = QtWidgets.QTableWidgetItem(pos_str)
            item_pos.setTextAlignment(QtCore.Qt.AlignCenter)
            item_pos.setForeground(QtGui.QColor("#2980b9"))  # Cor azulada para destaque
            self.table.setItem(row, 1, item_pos)
        else:
            # Tenta preencher a primeira célula vazia da coluna B
            found = False
            for r in range(self.table.rowCount()):
                item_b = self.table.item(r, 2)
                if item_b is None or item_b.text() == "":
                    item_pos = QtWidgets.QTableWidgetItem(pos_str)
                    item_pos.setTextAlignment(QtCore.Qt.AlignCenter)
                    item_pos.setForeground(QtGui.QColor("#27ae60"))  # Cor esverdeada
                    self.table.setItem(r, 2, item_pos)
                    found = True
                    break

            if not found:
                # Se não houver linha com A esperando, cria linha nova com B
                row = self.table.rowCount()
                self.table.insertRow(row)
                item_id = QtWidgets.QTableWidgetItem(f"P {row + 1}")
                item_id.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row, 0, item_id)

                item_pos = QtWidgets.QTableWidgetItem(pos_str)
                item_pos.setTextAlignment(QtCore.Qt.AlignCenter)
                item_pos.setForeground(QtGui.QColor("#27ae60"))
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