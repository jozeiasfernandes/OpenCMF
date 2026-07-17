from PySide6 import QtWidgets, QtCore
from typing import Dict, Optional


class SidePanelContainer(QtWidgets.QWidget):
    """
    Representa o container visual que hospeda os componentes laterais.
    """

    def __init__(self, title: str = "Inspector", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # Layout principal para garantir que o ScrollArea preencha todo o espaço
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Widget interno que conterá os painéis
        self._content_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout(self._content_widget)
        self._layout.setContentsMargins(5, 5, 5, 5)
        self._layout.setSpacing(5)
        self._layout.setAlignment(QtCore.Qt.AlignTop)

        # Scroll area para suportar muitos painéis
        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(self._content_widget)
        self._scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        # Adiciona o ScrollArea ao layout do container principal
        self.main_layout.addWidget(self._scroll)

        self.panels: Dict[str, QtWidgets.QWidget] = {}

    def add_panel(self, panel_id: str, panel: QtWidgets.QWidget):
        """Adiciona um painel ao container."""
        if panel_id in self.panels:
            self.remove_panel(panel_id)

        # Garante que o painel seja desvinculado de qualquer parent anterior
        panel.setParent(None)

        # Configura o parent para o widget de conteúdo e adiciona ao layout
        panel.setParent(self._content_widget)
        panel.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        self._layout.addWidget(panel)
        self.panels[panel_id] = panel
        panel.setVisible(True)

    def remove_panel(self, panel_id: str):
        """Remove um painel do container."""
        if panel := self.panels.pop(panel_id, None):
            # Chama o método dispose se for um BaseComponent
            if hasattr(panel, 'dispose'):
                panel.dispose()

            self._layout.removeWidget(panel)
            panel.setParent(None)
            panel.deleteLater()

    def clear_all(self):
        """Remove todos os painéis."""
        for panel_id in list(self.panels.keys()):
            self.remove_panel(panel_id)