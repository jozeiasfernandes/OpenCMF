from PySide6 import QtWidgets, QtCore, QtGui

from settings.icons.icons_manager import IconManager
from settings.settings_app_manager import settings


class HomeButton(QtWidgets.QToolButton):
    clicked_signal = QtCore.Signal()

    def __init__(self, icon_size: QtCore.QSize):
        super().__init__()
        self.icon_size_setting = icon_size

        self._configure_identity()
        self.update_icon()

        self.clicked.connect(self.clicked_signal.emit)

        # Conecta o sinal de mudança de tema de forma assíncrona
        QtCore.QTimer.singleShot(0, self._connect_theme_signal)

    def _configure_identity(self):
        self.setObjectName("botaoHomeWorkspace")
        self.setFixedSize(self.icon_size_setting)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setAutoRaise(True)

    def update_icon(self):
        """Atualiza o ícone utilizando o IconManager considerando o tema ativo."""
        theme = settings.get("preferencias", "tema", "dark")
        manager = IconManager.get_instance()
        cor_default = manager.get_color(theme, "status", "default")

        # Define o tamanho em pixels baseado no QSize passado
        size = self.icon_size_setting.width()
        icon = manager.get_icon("home", color=cor_default, size=size)

        if not icon.isNull():
            self.setIcon(icon)
            self.setIconSize(self.icon_size_setting)
        else:
            self._apply_fallback("Home")

    def _connect_theme_signal(self):
        """Conecta ao sinal de mudança de tema da janela principal se disponível."""
        if self.window() and hasattr(self.window(), 'theme_changed'):
            self.window().theme_changed.connect(self.update_icon)
        else:
            QtCore.QTimer.singleShot(500, self._connect_theme_signal)

    def _apply_fallback(self, text: str):
        """Aplica texto de fallback quando o ícone não está disponível."""
        self.setText(text)