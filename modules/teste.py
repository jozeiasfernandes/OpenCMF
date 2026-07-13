from typing import Dict
from PySide6 import QtWidgets, QtCore
from modules.base_module.base_module import ModuloBase


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Módulo de Teste"

    def get_main_widget(self) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)


        label = QtWidgets.QLabel("Módulo em branco pronto para desenvolvimento.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QPushButton("Ação de Exemplo"))

        return container

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        aba_ferramentas = QtWidgets.QWidget()
        lay_ferramentas = QtWidgets.QVBoxLayout(aba_ferramentas)
        lay_ferramentas.addWidget(QtWidgets.QPushButton("Ferramenta 1"))
        lay_ferramentas.addStretch()

        return {"Operações": aba_ferramentas}

    def cleanup(self) -> None:
        # Lógica de limpeza
        super().cleanup()


if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets, QtCore

    # 1. Inicializa a aplicação
    app = QtWidgets.QApplication(sys.argv)

    # 2. Instancia o seu módulo
    modulo = Modulo()

    # Opcional: Se o seu módulo tiver um método de inicialização, chame-o aqui
    # modulo.inicializar("caminho/do/projeto")

    # 3. Cria a janela principal de teste
    janela = QtWidgets.QMainWindow()
    janela.setWindowTitle(f"Teste: {modulo.nome}")
    janela.resize(1000, 700)

    # 4. Organiza a UI de forma similar ao ModuleLayoutBuilder
    container_principal = QtWidgets.QWidget()
    layout_principal = QtWidgets.QHBoxLayout(container_principal)

    # Splitter para simular a divisão entre Toolboxes e Main Widget
    splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

    # Adiciona as side_panel_container (o dicionário retornado por get_toolboxes)
    toolboxes = modulo.get_toolboxes()
    if toolboxes:
        toolbox_widget = QtWidgets.QWidget()
        layout_tb = QtWidgets.QVBoxLayout(toolbox_widget)
        for nome, widget in toolboxes.items():
            layout_tb.addWidget(QtWidgets.QLabel(f"<b>{nome}</b>"))
            layout_tb.addWidget(widget)
        layout_tb.addStretch()
        splitter.addWidget(toolbox_widget)

    # Adiciona o widget principal
    splitter.addWidget(modulo.get_main_widget())

    # Define o splitter no layout
    layout_principal.addWidget(splitter)
    janela.setCentralWidget(container_principal)

    janela.show()

    # 5. Executa
    try:
        sys.exit(app.exec())
    finally:
        # Garante que o método de limpeza seja chamado ao fechar
        modulo.cleanup()