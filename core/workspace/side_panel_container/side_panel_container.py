# core/workspace/side_panel_container/side_panel_container.py

from PySide6 import QtWidgets, QtCore
from typing import Dict, Optional
from core.components.bases.base_sidepanel import BaseSidePanel

class SidePanelContainer(QtWidgets.QDockWidget):
    """
    Representa o container visual que hospeda os componentes laterais.
    Gerencia o layout, scroll e a exibição dos painéis. [cite: 48]
    """

    def __init__(self, title: str = "Inspector", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(title, parent)

        # Widget base
        self._main_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout(self._main_widget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._layout.setAlignment(QtCore.Qt.AlignTop)

        # Scroll area para suportar muitos painéis [cite: 49]
        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(self._main_widget)
        self._scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.setWidget(self._scroll)
        self.panels: Dict[str, BaseSidePanel] = {}

    def add_panel(self, panel_id: str, panel: BaseSidePanel):
        if panel_id not in self.panels:
            self._layout.addWidget(panel)
            self.panels[panel_id] = panel # [cite: 50]

    def remove_panel(self, panel_id: str):
        if panel := self.panels.pop(panel_id, None):
            self._layout.removeWidget(panel)
            panel.deleteLater()