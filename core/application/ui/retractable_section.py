from PySide6 import QtWidgets, QtCore, QtGui


class Retractable_Section(QtWidgets.QWidget):
    def __init__(self, titulo, inicial_aberto=False, parent=None):
        super().__init__(parent)
        self.layout_principal = QtWidgets.QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 5, 0, 5)
        self.layout_principal.setSpacing(0)

        self.botao_toggle = QtWidgets.QPushButton(f"{'▼' if inicial_aberto else '▶'}  {titulo}")
        self.botao_toggle.setCheckable(True)
        self.botao_toggle.setChecked(inicial_aberto)

        self.botao_toggle.setStyleSheet("""
            QPushButton {
                text-align: left; 
                padding: 8px; 
                font-weight: bold;
                background-colors: #2c3e50; 
                colors: white; 
                border: 1px solid #34495e; 
                border-radius: 4px;
            }
            QPushButton:checked { 
                border-bottom-left-radius: 0px; 
                border-bottom-right-radius: 0px; 
            }
            QPushButton:hover {
                background-colors: #34495e;
            }
        """)

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