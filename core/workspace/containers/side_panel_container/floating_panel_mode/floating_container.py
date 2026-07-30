from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QScrollArea

from core.workspace.containers.side_panel_container.floating_panel_mode.collapsible_section_floating import CollapsibleSectionFloating
from core.settings.settings_app_manager import settings
from core.icons.icons_manager import IconManager


class FloatingContainer(QFrame):
    """Container flutuante que pode sobrepor a área central do workspace em modo toolbox,
    permitindo visualização e edição sem ocupar espaço horizontal fixo.
    """

    # Sinal emitido para solicitar o retorno ao modo fixo (toolbox/tabs)
    dock_requested = Signal()

    def __init__(self, parent: QWidget = None, title: str = "Painel Flutuante"):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setObjectName("FloatingContainer")
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Variáveis para controle de arraste (drag) da janela
        self._is_dragging = False
        self._drag_position = QPoint()

        self._setup_ui(title)

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
        self.close_btn.clicked.connect(self.hide)
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

    def set_content(self, widget: QWidget):
        """Define ou substitui o widget de conteúdo principal do container."""
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()

        if widget:
            self.content_layout.insertWidget(0, widget)

    def add_section(self, section_widget: QWidget):
        """Adiciona uma seção retrátil ao container flutuante."""
        count = self.content_layout.count()
        if count > 0:
            self.content_layout.insertWidget(count - 1, section_widget)
        else:
            self.content_layout.addWidget(section_widget)

    def add_section_by_title(self, title: str, content_widget: QWidget) -> CollapsibleSectionFloating:
        """Cria e adiciona uma CollapsibleSectionToolbox diretamente ao container flutuante."""
        section = CollapsibleSectionFloating(title, content_widget, self)
        self.add_section(section)
        return section

    def remove_section(self, section_widget: QWidget):
        """Remove uma seção do container flutuante."""
        self.content_layout.removeWidget(section_widget)
        section_widget.setParent(None)
        section_widget.deleteLater()

    def clear_sections(self):
        """Remove todas as seções do container flutuante."""
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()

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