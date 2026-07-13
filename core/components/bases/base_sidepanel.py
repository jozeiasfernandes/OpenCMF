from PySide6 import QtWidgets, QtCore
from typing import Optional, Any
from core.components.bases.base_component import BaseComponent


class BaseSidePanel(QtWidgets.QDockWidget, BaseComponent):
    """
    Base para painéis laterais. Herda de QDockWidget para permitir
    movimentação, flutuação e organização pelo usuário.
    """
    side_panel_name: str = "Painel Lateral Genérico"

    def __init__(self, context: Any, title: str, parent: Optional[QtWidgets.QWidget] = None):
        # Inicializa o QDockWidget (UI) e o BaseComponent (Lógica)
        QtWidgets.QDockWidget.__init__(self, title, parent)
        BaseComponent.__init__(self, context=context, parent=parent)

        # Configurações de Movimentação (Requisito)
        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )

        # Widget interno que conterá o layout do painel
        self.contents = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.contents)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.setWidget(self.contents)

    def setup_component(self):
        self.setup_ui()
        self._is_loaded = True

    def setup_ui(self) -> None:
        """Sobrescreva nas subclasses para adicionar widgets."""
        pass

    def add_widget_to_panel(self, widget: QtWidgets.QWidget):
        """Adiciona um item ao layout do painel."""
        self.layout.addWidget(widget)

    @property
    def event_bus(self):
        return self.scene_manager.events if self.scene_manager else None

    def get_ui(self) -> QtWidgets.QDockWidget:
        return self