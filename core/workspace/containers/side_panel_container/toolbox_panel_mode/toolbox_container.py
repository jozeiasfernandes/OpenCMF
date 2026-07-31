from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from typing import Dict, Optional
from core.workspace.containers.side_panel_container.base.base_side_panel_container import BaseSidePanelMode
from core.workspace.containers.side_panel_container.toolbox_panel_mode.collapsible_section_toolbox import \
    CollapsibleSectionToolbox


class ToolboxSidePanelMode(BaseSidePanelMode, QWidget):
    """Estratégia no Modo Toolbox com seções retráteis baseadas em CollapsibleSectionToolbox para o workspace."""

    def __init__(self, container: Optional[QWidget] = None):
        super().__init__(container)
        self.setObjectName("ToolboxContainer")

        # Mapeamento interno para rastrear painéis por ID com segurança
        self._panel_widgets: Dict[str, QWidget] = {}
        self._section_widgets: Dict[str, QWidget] = {}

        self._setup_ui()

        # Se um container pai foi passado, integra o widget no layout dele
        if container:
            layout = container.layout()
            if not layout:
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
            layout.addWidget(self)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Área de rolagem para acomodar múltiplas seções retráteis
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("ToolboxScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)

        # Container interno da scroll area
        self.content_widget = QWidget(self.scroll_area)
        self.content_widget.setObjectName("ToolboxContentWidget")

        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(6)
        self.content_layout.addStretch()  # Mantém os elementos empurrados para o topo

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

    def add_panel(self, panel_id: str, widget: QWidget, title: str):
        """Adiciona ou substitui um painel em formato de seção retrátil no toolbox."""
        if panel_id in self._panel_widgets:
            self.remove_panel(panel_id)

        self._panel_widgets[panel_id] = widget

        # Cria a seção retrátil do toolbox envolvendo o widget
        section = CollapsibleSectionToolbox(title, widget, self)
        self._section_widgets[panel_id] = section

        widget.setVisible(True)

        count = self.content_layout.count()
        if count > 0:
            self.content_layout.insertWidget(count - 1, section)
        else:
            self.content_layout.addWidget(section)

    def remove_panel(self, panel_id: str):
        """Remove a seção e o widget correspondente ao identificador informado."""
        self._panel_widgets.pop(panel_id, None)
        section = self._section_widgets.pop(panel_id, None)

        if section:
            self.content_layout.removeWidget(section)

            # Recupera e gerencia o widget interno se necessário
            content = getattr(section, "content_area", None)
            if content and hasattr(content, 'dispose') and callable(content.dispose):
                try:
                    content.dispose()
                except Exception:
                    pass

            section.setParent(None)
            section.deleteLater()

    def clear(self):
        """Remove todas as seções do toolbox e limpa os registros internos."""
        for panel_id in list(self._panel_widgets.keys()):
            self.remove_panel(panel_id)

    def get_widget_by_id(self, panel_id: str) -> Optional[QWidget]:
        """Retorna o widget associado ao ID do painel."""
        return self._panel_widgets.get(panel_id)