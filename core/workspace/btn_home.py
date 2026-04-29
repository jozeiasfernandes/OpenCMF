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
        icon_path = self.base_dir / "appearance" / "icons" / "home.png"

        if icon_path.exists():
            self.setIcon(QtGui.QIcon(str(icon_path)))
            self.setIconSize(self.icon_size_setting)
        else:
            self.setText("Home")