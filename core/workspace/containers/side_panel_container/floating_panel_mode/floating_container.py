from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget

from containers.side_panel_container.collapsible_section import CollapsibleSection
from core.settings.settings_app_manager import settings
from core.icons.icons_manager import IconManager


class FloatingContainer(QFrame):
    """Container flutuante que pode sobrepor a área central do workspace,

    permitindo visualização e edição sem ocupar espaço horizontal fixo.
    """

    # Sinal emitido para solicitar o retorno ao modo fixo (toolbox/tabs)
    dock_requested = Signal()

    def __init__(self, parent: QWidget = None, title: str = "Painel Flutuante"):
        super().__init__(parent)
        # CORREÇÃO: Utilizar Qt.Tool em vez de Qt.SubWindow para eliminar problemas de renderização e rastros gráficos
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

        # Carrega o ícone arrow_circle_right.svg de forma segura pelo IconManager
        icon_manager = IconManager.get_instance()
        dock_icon = icon_manager.get_icon("arrow_circle_right")
        if not dock_icon.isNull():
            self.dock_btn.setIcon(dock_icon)
        else:
            self.dock_btn.setText("➔")  # Fallback textual caso o ícone não carregue

        self.dock_btn.clicked.connect(self._on_dock_clicked)
        header_layout.addWidget(self.dock_btn)

        # Botão Fechar
        self.close_btn = QPushButton("✕", header_widget)
        self.close_btn.setObjectName("FloatingCloseButton")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.clicked.connect(self.hide)
        header_layout.addWidget(self.close_btn)

        layout.addWidget(header_widget)

        # Área de Conteúdo Interno
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        layout.addLayout(self.content_layout)

    def _on_dock_clicked(self):
        """Altera a configuração para o modo toolbox e solicita a reconstrução do painel."""
        settings.side_panel_mode = "toolbox"
        settings.save()
        self.dock_requested.emit()
        self.hide()

    def set_content(self, widget: QWidget):
        """Define ou substitui o widget de conteúdo principal do container."""
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        if widget:
            self.content_layout.addWidget(widget)

    def add_section(self, title: str, content_widget: QWidget) -> CollapsibleSection:
        """Adiciona diretamente uma seção retrátil (CollapsibleSection) ao container flutuante."""
        section = CollapsibleSection(title, content_widget, self)
        self.content_layout.addWidget(section)
        return section

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