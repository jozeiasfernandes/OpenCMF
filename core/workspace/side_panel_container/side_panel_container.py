from pathlib import Path
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

        panel.setParent(None)

        panel.setParent(self._content_widget)
        panel.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        self._layout.addWidget(panel)
        self.panels[panel_id] = panel
        panel.setVisible(True)

    def remove_panel(self, panel_id: str):
        if panel := self.panels.pop(panel_id, None):
            if hasattr(panel, 'dispose') and callable(panel.dispose):
                panel.dispose()

            self._layout.removeWidget(panel)
            panel.setParent(None)
            panel.deleteLater()

    def remover_widget_por_caminho(self, caminho: Path):
        """Remove um painel baseado na propriedade de caminho do módulo."""
        for panel_id, panel in list(self.panels.items()):
            mod_path = panel.property("__module_path__")
            if mod_path and Path(mod_path) == Path(caminho):
                self.remove_panel(panel_id)
                break

    def clear_all(self):
        """Remove todos os painéis."""
        for panel_id in list(self.panels.keys()):
            self.remove_panel(panel_id)