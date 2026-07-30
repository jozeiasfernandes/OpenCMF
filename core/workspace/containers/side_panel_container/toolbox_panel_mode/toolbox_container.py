from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from core.workspace.containers.side_panel_container.toolbox_panel_mode.collapsible_section_toolbox import CollapsibleSectionToolbox

class ToolboxContainer(QWidget):
    """Container em formato de Toolbox com seções retráteis baseadas em CollapsibleSectionTabs para o workspace."""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("ToolboxContainer")

        self._setup_ui()

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

    def add_section(self, section_widget: QWidget):
        """Adiciona uma seção retrátil ao toolbox."""
        count = self.content_layout.count()
        # Insere antes do stretch (que está na última posição se houver itens)
        if count > 0:
            self.content_layout.insertWidget(count - 1, section_widget)
        else:
            self.content_layout.addWidget(section_widget)

    def add_section_by_title(self, title: str, content_widget: QWidget) -> CollapsibleSectionToolbox:
        """Cria e adiciona uma CollapsibleSectionToolbox diretamente ao toolbox usando título e conteúdo."""
        section = CollapsibleSectionToolbox(title, content_widget, self)
        self.add_section(section)
        return section

    def remove_section(self, section_widget: QWidget):
        """Remove uma seção do toolbox."""
        self.content_layout.removeWidget(section_widget)
        section_widget.setParent(None)
        section_widget.deleteLater()

    def clear_sections(self):
        """Remove todas as seções do toolbox."""
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()