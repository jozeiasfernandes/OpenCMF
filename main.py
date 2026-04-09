import sys
from PySide6 import QtWidgets
from core.factory import ModuloFactory


def testar_carregamento():
    app = QtWidgets.QApplication(sys.argv)

    # 1. Tenta carregar o módulo de teste via Factory
    novo_modulo = ModuloFactory.carregar_modulo("mod_teste")

    if novo_modulo:
        # 2. Configura uma janela simples para exibir o resultado
        janela = QtWidgets.QMainWindow()
        janela.setWindowTitle("Teste de Carga Modular")
        janela.setMinimumSize(600, 400)

        # 3. Cria um layout para organizar o que veio do módulo
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)

        # Pegamos a área central e a toolbox do módulo carregado
        layout.addWidget(novo_modulo.get_workspace(), stretch=3)  # Área central maior
        layout.addWidget(novo_modulo.get_toolbox(), stretch=1)  # Toolbox lateral

        janela.setCentralWidget(container)
        janela.show()

        print("Módulo carregado com sucesso!")
        sys.exit(app.exec())
    else:
        print("Falha ao carregar o módulo. Verifique os nomes de arquivos e classes.")


if __name__ == "__main__":
    testar_carregamento()