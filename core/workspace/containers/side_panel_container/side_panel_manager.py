from pathlib import Path
from PySide6 import QtWidgets
from core.workspace.containers.side_panel_container.side_panel_container import SidePanelContainer
from settings.settings_app_manager import settings


class SidePanelManager:
    """Gerencia a interface do painel lateral, delegando as operações diretamente para o SidePanelContainer."""

    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.container = SidePanelContainer("Side Panel", workspace_manager=parent_window, parent=parent_window)

        # Configura a visibilidade inicial com base nas preferências
        current_mode = settings.side_panel_mode
        show_default = settings.side_panel_show_by_default

        if current_mode == "floating":
            self.container.setVisible(False)
            if self.container.floating_window and show_default:
                self.container.floating_window.show()
        else:
            self.container.setVisible(show_default)

    def add_panel(self, name: str, widget: QtWidgets.QWidget):
        """Adiciona um painel através do container principal."""
        panel_id = name.lower().replace(" ", "_")
        if hasattr(self.container, "add_panel"):
            self.container.add_panel(panel_id, widget, title=name)

            if settings.side_panel_mode == "floating":
                if self.container.floating_window and settings.side_panel_show_by_default:
                    self.container.floating_window.show()
                self.container.setVisible(False)
            else:
                self.container.setVisible(True)

            widget.setVisible(True)

    def remove_panel(self, name: str):
        """Remove um painel do container ativo."""
        panel_id = name.lower().replace(" ", "_")
        if hasattr(self.container, "remove_panel"):
            self.container.remove_panel(panel_id)

    def remover_widget_por_caminho(self, caminho: Path):
        """Repassa a solicitação de remoção por caminho para o container."""
        if hasattr(self.container, "remover_widget_por_caminho"):
            self.container.remover_widget_por_caminho(caminho)

    def clear_all(self):
        """Limpa todos os painéis e fecha a janela flutuante se ativa."""
        if hasattr(self.container, "clear_all"):
            self.container.clear_all()
        if self.container.floating_window:
            self.container.floating_window.hide()

    def atualizar_largura_painel(self, width: int):
        """Redimensiona a janela flutuante se o modo ativo for floating."""
        if settings.side_panel_mode == "floating" and self.container.floating_window:
            self.container.floating_window.resize(width, self.container.floating_window.height())

    def _criar_janela_flutuante(self):
        """Método auxiliar de compatibilidade que retorna a janela flutuante do container."""
        if not self.container.floating_window and hasattr(self.container, "_setup_floating_window"):
            self.container._setup_floating_window("Side Panel")
        return self.container.floating_window