from PySide6 import QtWidgets, QtCore
from typing import Optional, Any
from core.components.bases.base_component import BaseComponent


class BaseSidePanel(QtWidgets.QDockWidget):
    """
    Base para painéis laterais.
    Herda apenas de QDockWidget para garantir a inicialização correta do Qt.
    O BaseComponent é integrado por composição ou via inicialização explícita.
    """
    side_panel_name: str = "Painel Lateral Genérico"

    def __init__(self, context: Any, titulo: str, parent: Optional[QtWidgets.QWidget] = None):
        # 1. Inicializa o QDockWidget (UI) através do super()
        super().__init__(titulo, parent)

        # 2. Inicializa o BaseComponent como uma instância auxiliar (Composição)
        self._logic = BaseComponent(context=context, parent=self)
        self._is_loaded = False

        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )

        self.contents = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.contents)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.setWidget(self.contents)

        # Chamar setup_component automaticamente
        self.setup_component()

    # Delegamos métodos do BaseComponent para a instância self._logic
    @property
    def scene_manager(self):
        """Retorna o scene_manager do contexto."""
        return self._logic.scene_manager if hasattr(self, '_logic') else None

    @property
    def event_bus(self):
        """Retorna o event_bus do scene_manager."""
        return self.scene_manager.events if self.scene_manager else None

    @property
    def context(self):
        """Retorna o contexto."""
        return self._logic.context if hasattr(self, '_logic') else None

    def setup_component(self):
        """Configura o componente."""
        if self._is_loaded:
            return
        # CORRIGIDO: Não chamar _logic.setup_component() para evitar dupla chamada
        # Apenas chamamos setup_ui() diretamente
        self.setup_ui()
        self._is_loaded = True

    def setup_ui(self) -> None:
        """Método para ser sobrescrito pelas classes filhas."""
        pass

    def add_widget_to_panel(self, widget: QtWidgets.QWidget):
        """Adiciona um widget ao painel."""
        self.layout.addWidget(widget)

    def get_ui(self) -> QtWidgets.QDockWidget:
        """Retorna a interface."""
        return self

    def dispose(self):
        """Limpeza de recursos."""
        if hasattr(self, '_logic'):
            self._logic.dispose()
        self._is_loaded = False