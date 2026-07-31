from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import Signal
from PySide6 import QtWidgets, QtCore

class SidePanelDrawerMixin:
    """
    Mixin responsável por isolar a lógica de comportamento de "gaveta"
    (recolhimento e expansão lateral com ajuste dinâmico do QSplitter).
    """

    toggle_requested = QtCore.Signal(bool)

    def apply_drawer_state(self, collapsed: bool):
        """Oculta o conteúdo interno, ajusta a política e limites de largura e emite o sinal para o WorkspaceManager."""
        if hasattr(self, "content_container"):
            self.content_container.setVisible(not collapsed)

        policy = self.sizePolicy()

        if collapsed:
            # Fixa a política e as larguras restritas para exibir apenas a barra compacta
            policy.setHorizontalPolicy(QSizePolicy.Fixed)
            self.setMaximumWidth(45)
            self.setMinimumWidth(35)
        else:
            # Restaura a política expansível e libera os limites utilizando o valor máximo padrão do Qt (16777215)
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            self.setMaximumWidth(16777215)
            self.setMinimumWidth(100)

        self.setSizePolicy(policy)

        # Delega a responsabilidade de manipulação do QSplitter para a autoridade máxima (WorkspaceManager)
        self.toggle_requested.emit(collapsed)

    def _find_parent_splitter(self) -> QtWidgets.QSplitter:
        """Busca recursivamente o QSplitter pai na hierarquia de widgets."""
        splitter = self.parent()
        while splitter and not isinstance(splitter, QtWidgets.QSplitter):
            splitter = splitter.parent()
        return splitter