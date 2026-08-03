from PySide6 import QtWidgets, QtCore, QtGui


class SecaoRetratil(QtWidgets.QWidget):
    def __init__(self, titulo, inicial_aberto=False, parent=None):
        super().__init__(parent)
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 5, 0, 5)
        self.layout_principal.setSpacing(0)

        self.botao_toggle = QtWidgets.QPushButton(f"{'▼' if inicial_aberto else '▶'}  {titulo}")
        self.botao_toggle.setCheckable(True)
        self.botao_toggle.setChecked(inicial_aberto)

        self.conteudo = QtWidgets.QWidget()
        self.conteudo.setVisible(inicial_aberto)
        self.layout_conteudo = QtWidgets.QVBoxLayout(self.conteudo)
        self.layout_conteudo.setContentsMargins(10, 10, 10, 10)

        self.layout_principal.addWidget(self.botao_toggle)
        self.layout_principal.addWidget(self.conteudo)

        self.botao_toggle.toggled.connect(self.ao_alternar)

    def ao_alternar(self, checked):
        self.conteudo.setVisible(checked)
        texto_puro = self.botao_toggle.text()[2:]
        self.botao_toggle.setText(f"{'▼' if checked else '▶'}  {texto_puro}")

    def layout_interno(self):
        return self.layout_conteudo


def criar_linha_arquivo(edit_widget, callback_funcao, folder=True):
    widget_linha = QtWidgets.QWidget()
    layout_linha = QtWidgets.QHBoxLayout(widget_linha)
    layout_linha.setContentsMargins(0, 0, 0, 0)

    layout_linha.addWidget(edit_widget)

    botao_busca = QtWidgets.QToolButton()
    botao_busca.setText("...")
    botao_busca.setCursor(QtCore.Qt.PointingHandCursor)

    botao_busca.clicked.connect(lambda: callback_funcao(edit_widget, folder))

    layout_linha.addWidget(botao_busca)

    return widget_linha