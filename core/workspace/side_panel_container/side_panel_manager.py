from pathlib import Path
from PySide6 import QtWidgets
from core.workspace.side_panel_container.side_panel_container import SidePanelContainer
from core.settings.settings_app_manager import settings


class SidePanelManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.container = SidePanelContainer("Side Panel", parent_window)

        # Configura visibilidade inicial baseada nas preferências do usuário
        show_default = settings.side_panel_show_by_default
        self.container.setVisible(show_default)

    def add_panel(self, name: str, widget: QtWidgets.QWidget):
        """Adiciona um widget ao container lateral."""
        panel_id = name.lower().replace(" ", "_")
        if hasattr(self.container, "add_panel"):
            self.container.add_panel(panel_id, widget, title=name)
            self.container.setVisible(True)
            widget.setVisible(True)

    def remove_panel(self, name: str):
        """Remove um widget do painel lateral pelo ID/nome."""
        panel_id = name.lower().replace(" ", "_")
        if hasattr(self.container, "remove_panel"):
            self.container.remove_panel(panel_id)

    def remover_widget_por_caminho(self, caminho: Path):
        """Repassa a solicitação de remoção por caminho para o container interno."""
        if hasattr(self.container, "remover_widget_por_caminho"):
            self.container.remover_widget_por_caminho(caminho)

    def clear_all(self):
        """Limpa todos os painéis."""
        if hasattr(self.container, "clear_all"):
            self.container.clear_all()

    def atualizar_largura_painel(self, width: int):
        """Repassa a solicitação de largura para o container interno."""
        if hasattr(self.container, "atualizar_largura"):
            self.container.atualizar_largura(width)