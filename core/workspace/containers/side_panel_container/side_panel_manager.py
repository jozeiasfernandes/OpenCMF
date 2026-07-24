from pathlib import Path
from PySide6 import QtWidgets
from core.workspace.containers.side_panel_container.side_panel_container import SidePanelContainer
from core.workspace.containers.side_panel_container.floating_panel_mode.floating_container import FloatingContainer
from core.settings.settings_app_manager import settings


class SidePanelManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.container = SidePanelContainer("Side Panel", parent_window)
        self.floating_window = None

        # Verifica o modo atual de exibição
        current_mode = settings.side_panel_mode
        show_default = settings.side_panel_show_by_default

        if current_mode == "floating":
            self.container.setVisible(False)
            # Inicializa o container flutuante de forma oculta por padrão, aguardando painéis
            self._setup_floating_window()
        else:
            self.container.setVisible(show_default)

    def _setup_floating_window(self):
        """Configura a janela flutuante se o modo for floating."""
        if not self.floating_window:
            self.floating_window = FloatingContainer(self.parent_window, title="Side Panel")
            # Define o conteúdo do container flutuante com a estrutura interna do container lateral
            self.floating_window.set_content(self.container.content_container)
            self.floating_window.resize(300, 400)  # Tamanho inicial padrão seguro para o flutuante

    def add_panel(self, name: str, widget: QtWidgets.QWidget):
        """Adiciona um widget ao container lateral ou ao painel flutuante."""
        panel_id = name.lower().replace(" ", "_")
        if hasattr(self.container, "add_panel"):
            self.container.add_panel(panel_id, widget, title=name)

            if settings.side_panel_mode == "floating":
                self._setup_floating_window()
                if settings.side_panel_show_by_default:
                    self.floating_window.show()
                self.container.setVisible(False)
            else:
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
        """Limpa todos os painéis e oculta a janela flutuante se ativa."""
        if hasattr(self.container, "clear_all"):
            self.container.clear_all()
        if self.floating_window:
            self.floating_window.hide()

    def atualizar_largura_painel(self, width: int):
        """Método mantido por compatibilidade; redimensionamento lateral agora ocorre via QSplitter."""
        if settings.side_panel_mode == "floating" and self.floating_window:
            self.floating_window.resize(width, self.floating_window.height())

    def _criar_janela_flutuante(self):
        if not self.floating_window:
            self.floating_window = FloatingContainer(self.parent_window)
            # Conecta o sinal de reanexar à função de reconstrução da workspace
            if hasattr(self.parent_window, "reconstruir_side_panel"):
                self.floating_window.dock_requested.connect(
                    self.parent_window.reconstruir_side_panel
                )
        return self.floating_window