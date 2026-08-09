from PySide6 import QtWidgets, QtCore
from typing import Optional, Any
from application.scene.scene_manager import SceneManager
from application.scene.events.scene_events import SceneEvents
from core.components.bases.base_sidepanel import BaseSidePanel


class Registration_SidePanel(BaseSidePanel):
    side_panel_name = "Alinhar Objetos"

    solicitarAlinhamento = QtCore.Signal()
    limparPontos = QtCore.Signal()
    targetChanged = QtCore.Signal(str)
    sourceChanged = QtCore.Signal(str)

    def __init__(self, context: Any, title: str = "", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, title=title, parent=parent)
        self._is_initializing = False

        # Verifica se event_bus existe no _logic (que é o BaseComponent)
        if hasattr(self._logic, 'event_bus') and self._logic.event_bus:
            self._logic.event_bus.subscribe(SceneEvents.OBJECT_ADDED, self._refresh_scene_data)
            self._logic.event_bus.subscribe(SceneEvents.OBJECT_REMOVED, self._refresh_scene_data)

    def setup_ui(self) -> None:
        """Configura a interface (sobrescrita da BaseSidePanel)."""
        self.layout.setSpacing(10)

        group_sel = QtWidgets.QGroupBox("Seleção de Malhas")
        layout_sel = QtWidgets.QFormLayout(group_sel)

        self.combo_target = QtWidgets.QComboBox()
        self.combo_source = QtWidgets.QComboBox()
        self.combo_target.currentTextChanged.connect(self._on_target_changed)
        self.combo_source.currentTextChanged.connect(self._on_source_changed)

        layout_sel.addRow("Referência (Fix):", self.combo_target)
        layout_sel.addRow("Móvel (Source):", self.combo_source)
        self.layout.addWidget(group_sel)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Ponto", "Vista A", "Vista B"])
        self.layout.addWidget(self.table)

        # --- CORREÇÃO: Criar e adicionar os botões ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_clear = QtWidgets.QPushButton("Limpar Pontos")
        self.btn_align = QtWidgets.QPushButton("Alinhar objetos")

        # Conexões
        self.btn_clear.clicked.connect(self.limparPontos.emit)
        self.btn_align.clicked.connect(self.solicitarAlinhamento.emit)

        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_align)
        self.layout.addLayout(btn_layout)

        self._refresh_scene_data()

    @property
    def scene_manager(self) -> Optional[SceneManager]:
        """Acesso seguro ao gerenciador de cena."""
        return getattr(self, '_scene_manager', None)

    def _on_target_changed(self, texto):
        if not self._is_initializing:
            if texto == self.combo_source.currentText() and texto != "":
                self.combo_source.blockSignals(True)
                self.combo_source.setCurrentIndex(0)  # Seleciona o vazio
                self.combo_source.blockSignals(False)

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
        if not hasattr(self, 'combo_target'):
            return

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
        return self.combo_target.currentText() if hasattr(self, 'combo_target') else ""

    def get_source_name(self):
        return self.combo_source.currentText() if hasattr(self, 'combo_source') else ""

    def limpar_tabela(self):
        if hasattr(self, 'table'):
            self.table.setRowCount(0)

    def _refresh_scene_data(self, **kwargs):
        """Atualiza a lista de objetos de forma segura."""
        if not self.scene_manager or not hasattr(self, 'combo_target'):
            return

        objs = getattr(self.scene_manager.objects, 'all', lambda: [])()
        nomes = [obj.name for obj in objs]
        self.atualizar_combos(nomes)


if __name__ == "__main__":
    import sys
    from unittest.mock import MagicMock

    app = QtWidgets.QApplication(sys.argv)
    mock_ctx = MagicMock()

    panel = Registration_SidePanel(context=mock_ctx, title="")

    panel.resize(300, 400)
    panel.show()

    sys.exit(app.exec())