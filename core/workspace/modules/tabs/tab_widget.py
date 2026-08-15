# Apresentação visual e interação direta de uma aba individual
from PySide6 import QtWidgets, QtCore


class WorkspaceTabWidget(QtWidgets.QFrame):
    close_requested = QtCore.Signal()
    clicked = QtCore.Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)  # Melhor UX
        self._is_active = False

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(8, 2, 8, 2)

        self.title_label = QtWidgets.QLabel(title)

        # Configuração do botão de fechar (visibilidade controlada via QSS)
        self.close_button = QtWidgets.QPushButton("×")
        self.close_button.setFixedSize(16, 16)
        self.close_button.setObjectName("TabCloseButton")
        self.close_button.clicked.connect(self.close_requested.emit)

        self.layout.addWidget(self.title_label)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.close_button)

        self._update_style()

    def _update_style(self):
        """Atualiza a propriedade dinâmica para estilização via QSS."""
        self.setProperty("ativo", "true" if self._is_active else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        # O hover visual é gerenciado pelo QSS (:hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        super().leaveEvent(event)

    def set_active(self, active: bool):
        self._is_active = active
        self._update_style()