from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QScrollArea
from typing import Dict, Optional

from core.workspace.containers.side_panel_container.base.base_side_panel_container import BaseSidePanelMode
from core.workspace.containers.side_panel_container.floating_panel_mode.collapsible_section_floating import \
    CollapsibleSectionFloating
from core.settings.settings_app_manager import settings
from core.settings.icons.icons_manager import IconManager


class FloatingSidePanelMode(BaseSidePanelMode, QFrame):
    """
    Estratégia no Modo Floating (Flutuante) que pode sobrepor a área central do workspace,
    permitindo visualização e edição sem ocupar espaço horizontal fixo.
    """

    # Sinal emitido para solicitar o retorno ao modo fixo (toolbox/tabs)
    dock_requested = Signal()

    # Sinal emitido quando o painel flutuante é fechado/ocultado, evitando dessincronia visual
    closed = Signal()

    def __init__(self, container: Optional[QWidget] = None, title: str = "Painel Flutuante", parent: Optional[QWidget] = None):
        QFrame.__init__(self, parent)
        BaseSidePanelMode.__init__(self, container)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setObjectName("FloatingContainer")
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Variáveis para controle de arraste (drag) da janela
        self._is_dragging = False
        self._drag_position = QPoint()

        # Mapeamento interno para rastrear painéis por ID com segurança
        self._panel_widgets: Dict[str, QWidget] = {}
        self._section_widgets: Dict[str, QWidget] = {}

        self._setup_ui(title)

        # Se um container pai foi passado, integra o frame no layout dele
        if container:
            layout = container.layout()
            if not layout:
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
            layout.addWidget(self)

    def _setup_ui(self, title: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        # Cabeçalho do Container Flutuante (Barra de Título e Botões)
        header_widget = QWidget(self)
        header_widget.setObjectName("FloatingHeader")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 4, 8, 4)

        self.title_label = QLabel(title, header_widget)
        self.title_label.setObjectName("FloatingTitleLabel")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Botão para reanexar à workspace (Modo Toolbox)
        self.dock_btn = QPushButton(header_widget)
        self.dock_btn.setObjectName("FloatingDockButton")
        self.dock_btn.setFixedSize(24, 24)
        self.dock_btn.setToolTip("Reanexar à Workspace")

        icon_manager = IconManager.get_instance()
        dock_icon = icon_manager.get_icon("arrow_circle_right")
        if not dock_icon.isNull():
            self.dock_btn.setIcon(dock_icon)
        else:
            self.dock_btn.setText("➔")

        self.dock_btn.clicked.connect(self._on_dock_clicked)
        header_layout.addWidget(self.dock_btn)

        # Botão Fechar
        self.close_btn = QPushButton("✕", header_widget)
        self.close_btn.setObjectName("FloatingCloseButton")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.clicked.connect(self._on_close_clicked)
        header_layout.addWidget(self.close_btn)

        layout.addWidget(header_widget)

        # Área de Rolagem alinhada ao ToolboxContainer
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("FloatingScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)

        self.content_widget = QWidget(self.scroll_area)
        self.content_widget.setObjectName("FloatingContentWidget")

        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(6)
        self.content_layout.addStretch()  # Mantém os elementos empurrados para o topo

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

    def _on_dock_clicked(self):
        """Altera a configuração para o modo toolbox e solicita a reconstrução do painel."""
        settings.side_panel_mode = "toolbox"
        settings.save()
        self.dock_requested.emit()
        self.hide()

    def _on_close_clicked(self):
        """Manipula o fechamento do painel flutuante pelo botão X ou equivalente."""
        settings.side_panel_mode = "toolbox"
        settings.save()
        self.closed.emit()
        self.hide()

    def closeEvent(self, event):
        """Garante que o evento de fechamento nativo da janela dispare a sincronização."""
        self._on_close_clicked()
        super().closeEvent(event)

    def add_panel(self, panel_id: str, widget: QWidget, title: str):
        """Adiciona ou substitui um painel em formato de seção retrátil no container flutuante."""
        if panel_id in self._panel_widgets:
            self.remove_panel(panel_id)

        self._panel_widgets[panel_id] = widget

        # Cria a seção retrátil envolvendo o widget
        section = CollapsibleSectionFloating(title, widget, self)
        self._section_widgets[panel_id] = section

        widget.setVisible(True)

        count = self.content_layout.count()
        if count > 0:
            self.content_layout.insertWidget(count - 1, section)
        else:
            self.content_layout.addWidget(section)

    def remove_panel(self, panel_id: str):
        """Remove apenas a seção visual, preservando o widget interno no cache."""
        self._panel_widgets.pop(panel_id, None)
        section = self._section_widgets.pop(panel_id, None)

        if section:
            self.content_layout.removeWidget(section)

            # Desvincula o widget interno da seção antes de destruir a seção,
            if hasattr(section, "content_area") and section.content_area:
                section.content_area.setParent(None)

            section.setParent(None)
            section.deleteLater()

    def clear(self):
        """Remove todas as seções e limpa os registros internos."""
        for panel_id in list(self._panel_widgets.keys()):
            self.remove_panel(panel_id)

    def get_widget_by_id(self, panel_id: str) -> Optional[QWidget]:
        """Retorna o widget associado ao ID do painel."""
        return self._panel_widgets.get(panel_id)

    def set_title(self, title: str):
        """Atualiza o texto do título do painel flutuante."""
        self.title_label.setText(title)

    def mousePressEvent(self, event):
        """Permite iniciar o arraste do container ao clicar no cabeçalho."""
        if event.button() == Qt.LeftButton:
            if event.position().y() <= 40:
                self._is_dragging = True
                self._drag_position = (
                        event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                event.accept()

    def mouseMoveEvent(self, event):
        """Move o container flutuante conforme o mouse é arrastado."""
        if self._is_dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Finaliza o arraste do container."""
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()