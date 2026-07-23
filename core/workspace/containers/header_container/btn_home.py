from pathlib import Path

from PySide6 import QtWidgets, QtCore, QtGui


class HomeButton(QtWidgets.QToolButton):
    clicked_signal = QtCore.Signal()

    def __init__(self, base_dir: Path, icon_size: QtCore.QSize):
        super().__init__()
        self.base_dir = base_dir
        self.icon_size_setting = icon_size

        self._configure_identity()
        self._apply_icon_or_fallback()

        self.clicked.connect(self.clicked_signal.emit)

    def _configure_identity(self):
        self.setObjectName("botaoHomeWorkspace")
        self.setFixedSize(self.icon_size_setting)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def _apply_icon_or_fallback(self):
        icon_path = self.base_dir / "appearance" / "icons" / "home.svg"

        if icon_path.exists():
            icon = QtGui.QIcon(str(icon_path))
            if not icon.isNull():
                self.setIcon(icon)
                self.setIconSize(self.icon_size_setting)
                return

        # Fallback caso o ícone não seja encontrado ou seja inválido
        self._apply_fallback("Home")

    def _apply_fallback(self, text: str):
        """Aplica texto de fallback quando o ícone não está disponível."""
        self.setText(text)
        self.setStyleSheet("color: gray; font-size: 10px;")