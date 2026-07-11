from PySide6 import QtWidgets, QtCore, QtGui


class WorkspaceTabWidget(QtWidgets.QFrame):
    close_requested = QtCore.Signal()
    clicked = QtCore.Signal()
    insert_requested = QtCore.Signal(int)

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._is_active = False

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(8, 2, 8, 2)

        self.title_label = QtWidgets.QLabel(title)
        self.close_button = QtWidgets.QPushButton("×")
        self.close_button.hide()

        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addWidget(self.close_button)

        self.close_button.clicked.connect(self.close_requested.emit)

        self.setStyleSheet("background-color: #E0E0E0; border-radius: 4px;")

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Dispara quando o mouse entra na aba."""
        self.close_button.show()
        self.setStyleSheet("background-color: #D0D0D0; border: 1px solid #999;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Dispara quando o mouse sai da aba."""
        if not self._is_active:
            self.close_button.hide()
            self.setStyleSheet("background-color: #E0E0E0; border: none;")
        super().leaveEvent(event)

    def set_active(self, active: bool):
        self._is_active = active
        if active:
            self.setStyleSheet("background-color: #FFFFFF; border-bottom: 2px solid #0078D7;")
            self.close_button.show()
        else:
            self.setStyleSheet("background-color: #E0E0E0;")