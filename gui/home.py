from PySide6 import QtWidgets, QtCore


class PaginaHome(QtWidgets.QWidget):
    projeto_selecionado = QtCore.Signal(str)
    editor_solicitado = QtCore.Signal()

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)

        self.btn_projeto = QtWidgets.QPushButton("Abrir Projeto Ortognática - Home")
        self.btn_projeto.setFixedWidth(250)
        self.btn_projeto.clicked.connect(lambda: self.projeto_selecionado.emit("fluxos/ortog.json"))

        self.btn_editor = QtWidgets.QPushButton("Configurações de Fluxo")
        self.btn_editor.setFixedWidth(250)
        self.btn_editor.clicked.connect(self.editor_solicitado.emit)

        layout.addStretch()
        layout.addWidget(self.btn_projeto, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.btn_editor, alignment=QtCore.Qt.AlignCenter)
        layout.addStretch()