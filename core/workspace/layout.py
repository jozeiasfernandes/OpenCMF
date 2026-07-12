from PySide6 import QtWidgets, QtCore
from .contracts import IModule


class ModuleLayoutBuilder:
    def build(self, module: IModule) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        # Define o layout principal para o container
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Obtém o widget principal do módulo (garantido pela interface)
        viewport = module.get_main_widget()

        # Obtém os side_panel
        toolboxes = module.get_toolboxes()

        # Cria o splitter que divide a área entre side_panel e viewport
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Se houver side_panel, constrói o painel lateral
        if toolboxes:
            toolbox_widget = QtWidgets.QWidget()
            toolbox_layout = QtWidgets.QVBoxLayout(toolbox_widget)
            toolbox_layout.setContentsMargins(5, 5, 5, 5)

            for name, widget in toolboxes.items():
                toolbox_layout.addWidget(widget)

            toolbox_layout.addStretch()
            splitter.addWidget(toolbox_widget)
            # Define o tamanho fixo ou preferencial para o toolbox, se necessário
            splitter.setStretchFactor(0, 0)

            # Adiciona o widget principal ao splitter
        splitter.addWidget(viewport)
        splitter.setStretchFactor(1, 1)  # O viewport ocupa o restante do espaço

        layout.addWidget(splitter)
        return container

    def refresh(self, container: QtWidgets.QWidget, config: dict):
        """Opcional: implementar lógica de atualização de layout aqui."""
        pass