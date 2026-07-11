from PySide6 import QtWidgets, QtCore
from modules.base_module.base_module import ModuloBase
# Importe o protocolo para garantir a tipagem (opcional, mas recomendado)
from core.workspace.contracts import IModule

class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()


    def get_main_widget(self) -> QtWidgets.QWidget:
        # Substitui o get_workspace
        label = QtWidgets.QLabel("ÁREA DE TRAÇADO CEFALOMÉTRICO 2D/3D")
        label.setAlignment(QtCore.Qt.AlignCenter)
        return label

    def get_toolboxes(self) -> dict[str, QtWidgets.QWidget]:
        # Substitui o get_toolbox. O layout builder espera um dicionário.
        # Isso permite que o sistema organize múltiplos painéis se necessário.
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QtWidgets.QLabel("Pontos Anatômicos:"))
        layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Násio (N)"))
        layout.addWidget(QtWidgets.QPushButton("Marcar Ponto Sela (S)"))
        layout.addStretch()

        return {"Ferramentas": widget}

    def cleanup(self) -> None:
        # Necessário para liberar recursos ao fechar o módulo
        print("Limpeza do módulo de Cefalometria realizada.")


if __name__ == "__main__":
    import sys

    # Criação da aplicação necessária para qualquer interface PySide6
    app = QtWidgets.QApplication(sys.argv)

    # Instancia o seu módulo
    modulo = Modulo()

    # Cria uma janela principal para envolver o módulo
    # Isso simula o comportamento da aplicação host
    janela = QtWidgets.QMainWindow()
    janela.setWindowTitle("Teste do Módulo: Cefalometria")
    janela.resize(800, 600)

    # Configura o layout da janela com o workspace e a toolbox
    central_widget = QtWidgets.QWidget()
    layout_principal = QtWidgets.QHBoxLayout(central_widget)

    layout_principal.addWidget(modulo.get_toolbox(), stretch=1)
    layout_principal.addWidget(modulo.get_workspace(), stretch=3)

    janela.setCentralWidget(central_widget)

    # Exibe a janela
    janela.show()

    # Executa o loop de eventos
    sys.exit(app.exec())