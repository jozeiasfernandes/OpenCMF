from PySide6 import QtWidgets, QtCore
from typing import Dict, Optional


class SidePanelContainer(QtWidgets.QDockWidget):
    """
    Representa o container visual que hospeda os componentes laterais.
    """

    def __init__(self, title: str = "Inspector", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(title, parent)

        # 1. FIX: Desativar recursos de flutuação e fechamento pelo usuário
        # Isso impede que o painel saia do layout do Splitter
        self.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)

        # Widget base com layout vertical
        self._main_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout(self._main_widget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._layout.setAlignment(QtCore.Qt.AlignTop)

        # Scroll area para suportar muitos painéis
        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(self._main_widget)
        self._scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.setWidget(self._scroll)
        self.panels: Dict[str, QtWidgets.QWidget] = {}

        # Forçar visibilidade
        self.setVisible(True)

    def add_panel(self, panel_id: str, panel: QtWidgets.QWidget):
        """Adiciona um painel ao container."""
        if panel_id in self.panels:
            self.remove_panel(panel_id)

        # FIX: Garante que o painel é removido de qualquer parent anterior
        # antes de ser movido para este container.
        panel.setParent(None)

        # Configurar o panel
        panel.setParent(self._main_widget)
        panel.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        # Adicionar ao layout
        self._layout.addWidget(panel)
        self.panels[panel_id] = panel
        panel.setVisible(True)

        # Forçar atualização do layout
        self._layout.activate()

    def remove_panel(self, panel_id: str):
        """Remove um painel do container."""
        if panel := self.panels.pop(panel_id, None):
            self._layout.removeWidget(panel)
            panel.setParent(None)
            panel.deleteLater()
            self._layout.activate()

    def clear_all(self):
        """Remove todos os painéis."""
        for panel_id in list(self.panels.keys()):
            self.remove_panel(panel_id)