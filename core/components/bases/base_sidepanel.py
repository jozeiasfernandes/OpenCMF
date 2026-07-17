from PySide6 import QtWidgets, QtCore
from typing import Optional, Any
from core.components.bases.base_component import BaseComponent

# MUDANÇA: Herda de QWidget, não de QDockWidget
class BaseSidePanel(QtWidgets.QWidget):
    """
    Base para painéis laterais.
    Refatorado para ser um QWidget puro, compatível com layouts internos (QSplitter/VBoxLayout).
    """
    side_panel_name: str = "Painel Lateral Genérico"

    def __init__(self, context: Any, title: str, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # O 'title' pode ser guardado se você quiser exibir um cabeçalho customizado
        self.title = title

        # Inicializa o BaseComponent
        self._logic = BaseComponent(context=context, parent=self)
        self._is_loaded = False

        # Configuração do layout principal do painel
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Opcional: Adicionar um título visível no topo do painel,
        # já que perdemos a barra de título do QDockWidget
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; padding: 2px;")
        self.layout.addWidget(self.title_label)

        # Chamar setup_component automaticamente
        self.setup_component()

    # --- As propriedades @property podem permanecer iguais ---

    def setup_component(self):
        """Configura o componente."""
        if self._is_loaded:
            return
        self.setup_ui()
        self._is_loaded = True

    def setup_ui(self) -> None:
        """Método para ser sobrescrito pelas classes filhas."""
        pass

    def add_widget_to_panel(self, widget: QtWidgets.QWidget):
        """Adiciona um widget ao painel."""
        self.layout.addWidget(widget)

    def get_ui(self) -> QtWidgets.QWidget: # Mudou de QDockWidget para QWidget
        return self

    def dispose(self):
        """Limpeza de recursos."""
        if hasattr(self, '_logic'):
            self._logic.dispose()
        self._is_loaded = False

    @property
    def has_scene(self) -> bool:
        return self.scene_manager is not None