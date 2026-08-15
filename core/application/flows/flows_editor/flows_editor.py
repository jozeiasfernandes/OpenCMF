from PySide6 import QtWidgets, QtCore

class PaginaEditorFluxo(QtWidgets.QWidget):
    voltar_solicitado = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Cabeçalho com botão voltar
        header = QtWidgets.QHBoxLayout()
        btn_voltar = QtWidgets.QPushButton("← Voltar")
        btn_voltar.setFixedWidth(80)
        btn_voltar.clicked.connect(self.voltar_solicitado.emit)

        titulo = QtWidgets.QLabel("EDITOR DE FLUXOS")
        titulo.setStyleSheet("font-size: 14px; font-weight: bold;")

        header.addWidget(btn_voltar)
        header.addStretch()
        header.addWidget(titulo)
        header.addStretch()

        layout.addLayout(header)

        # Área Central (Representando o rascunho do editor de módulos)
        self.canvas = QtWidgets.QFrame()
        self.canvas.setStyleSheet("background-colors: #1e1e1e; border: 1px solid #333; border-radius: 4px;")

        # Simulação visual do flows (Quadrados e Setas)
        canvas_layout = QtWidgets.QHBoxLayout(self.canvas)
        canvas_layout.setSpacing(20)

        # Exemplo visual do flows conforme sua imagem de referência
        for i in range(3):
            modulo_item = self._criar_box_modulo(f"Módulo {i + 1}")
            canvas_layout.addWidget(modulo_item)
            if i < 2:
                canvas_layout.addWidget(QtWidgets.QLabel("→"))

        layout.addWidget(self.canvas)

    def _criar_box_modulo(self, nome):
        box = QtWidgets.QFrame()
        box.setFixedSize(120, 100)
        box.setStyleSheet("background-colors: #2d2d2d; border: 2px solid #555; border-radius: 8px;")

        l = QtWidgets.QVBoxLayout(box)
        l.addWidget(QtWidgets.QLabel(nome), alignment=QtCore.Qt.AlignCenter)
        l.addWidget(QtWidgets.QPushButton("+"), alignment=QtCore.Qt.AlignCenter)

        return box

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    janela = PaginaEditorFluxo()
    janela.setWindowTitle("Teste de Editor de Fluxos")
    janela.resize(800, 500)
    janela.show()

    sys.exit(app.exec())