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

        # Estilização básica do botão de fechar
        self.close_button = QtWidgets.QPushButton("×")
        self.close_button.setFixedSize(16, 16)
        self.close_button.setStyleSheet("border: none; color: #555; font-weight: bold;")
        self.close_button.hide()
        self.close_button.clicked.connect(self.close_requested.emit)

        self.layout.addWidget(self.title_label)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.close_button)

        self._update_style()

    def _update_style(self):
        """Centraliza a lógica de cores para evitar repetição."""
        if self._is_active:
            self.setStyleSheet("background-color: #FFFFFF; border-bottom: 2px solid #0078D7; border-radius: 0px;")
        else:
            self.setStyleSheet("background-color: #E0E0E0; border: none; border-radius: 4px;")

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.close_button.show()
        if not self._is_active:
            self.setStyleSheet("background-color: #D0D0D0; border: none; border-radius: 4px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._is_active:
            self.close_button.hide()
            self._update_style()
        super().leaveEvent(event)

    def set_active(self, active: bool):
        self._is_active = active
        self.close_button.setVisible(True)  # Sempre mostrar se ativa
        self._update_style()