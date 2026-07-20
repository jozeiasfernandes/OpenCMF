from PySide6 import QtWidgets, QtCore
from typing import Optional, Any
from core.components.bases.base_component import BaseComponent


class BaseSidePanel(QtWidgets.QWidget):
    """
    Base para painéis laterais.
    Refatorado para ser um QWidget puro, utilizando BaseComponent por composição
    para injeção de dependência e ciclo de vida, alinhado à nova flag '_loaded'.
    """
    side_panel_name: str = "Painel Lateral Genérico"

    def __init__(self, context: Any, title: str, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self.title = title

        # Composição com BaseComponent para injeção de contexto e serviços globais
        self._logic = BaseComponent(context=context, parent=self)

        # Configuração do layout principal do painel
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Cabeçalho visível no topo do painel
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; padding: 2px;")
        self.layout.addWidget(self.title_label)

        # Chamar setup_component automaticamente
        self.setup_component()

    @property
    def context(self) -> Optional[Any]:
        """Retorna o contexto atual injetado."""
        return self._logic.context if hasattr(self, '_logic') else None

    @property
    def scene_manager(self) -> Optional[Any]:
        """Retorna o scene_manager de forma segura."""
        return self._logic.scene_manager if hasattr(self, '_logic') else None

    @property
    def tool_manager(self) -> Optional[Any]:
        """Atalho seguro para o tool_manager."""
        return self._logic.tool_manager if hasattr(self, '_logic') else None

    @property
    def event_bus(self) -> Optional[Any]:
        """Atalho seguro para o event_bus."""
        if hasattr(self._logic, 'event_bus') and self._logic.event_bus:
            return self._logic.event_bus
        return None

    @property
    def has_scene(self) -> bool:
        """Verifica se há um scene_manager ativo."""
        return self.scene_manager is not None

    def setup_component(self) -> None:
        """Configura o componente utilizando a flag '_loaded' da BaseComponent."""
        if hasattr(self, '_logic') and self._logic._loaded:
            return

        self.setup_ui()

        if hasattr(self, '_logic'):
            self._logic._loaded = True

    def setup_ui(self) -> None:
        """Método para ser sobrescrito pelas classes filhas."""
        pass

    def add_widget_to_panel(self, widget: QtWidgets.QWidget) -> None:
        """Adiciona um widget ao painel."""
        self.layout.addWidget(widget)

    def get_ui(self) -> QtWidgets.QWidget:
        """Retorna a própria instância do painel."""
        return self

    def dispose(self) -> None:
        """Limpeza de recursos do painel e do logic."""
        if hasattr(self, '_logic'):
            self._logic.dispose()