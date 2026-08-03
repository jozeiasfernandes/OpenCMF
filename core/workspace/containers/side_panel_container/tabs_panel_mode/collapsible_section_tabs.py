from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from list_paths import ICONS_DIR


class CollapsibleSectionTabs(QtWidgets.QWidget):
    """
    Componente adaptado para o Modo Tabs do painel lateral.
    Gerencia seções orientadas a abas verticais e ícones padronizados.
    """

    def __init__(self, title: str, content_widget: QtWidgets.QWidget, parent=None):
        super().__init__(parent)

        # Utilizando a arquitetura centralizada do list_paths
        self.assets_dir = ICONS_DIR

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header Layout (Puxador + Título + Botão de Expandir/Recolher com ícone SVG)
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(4, 2, 4, 2)
        header_layout.setSpacing(6)

        # Puxador (Grip) usando drag_indicator.svg
        self.btn_grip = QtWidgets.QLabel()
        self.btn_grip.setCursor(QtCore.Qt.SizeVerCursor)
        self.btn_grip.setToolTip("Arraste para mover")

        drag_icon_path = self.assets_dir / "drag_indicator.svg"
        if drag_icon_path.exists():
            pixmap_grip = QtGui.QPixmap(str(drag_icon_path))
            if not pixmap_grip.isNull():
                self.btn_grip.setPixmap(
                    pixmap_grip.scaled(16, 16, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        self.lbl_title = QtWidgets.QLabel(title)
        self.lbl_title.setStyleSheet("font-weight: bold;")

        # Botão de Ocultar/Reexibir usando arrow_up.svg / arrow_down.svg
        self.toggle_button = QtWidgets.QToolButton()
        self.toggle_button.setStyleSheet("""
            QToolButton {
                border: none;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 3px;
            }
        """)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setCursor(QtCore.Qt.PointingHandCursor)

        self.icon_up_path = self.assets_dir / "arrow_up.svg"
        self.icon_down_path = self.assets_dir / "arrow_down.svg"

        self._update_toggle_icon(True)

        header_layout.addWidget(self.btn_grip)
        header_layout.addWidget(self.lbl_title, stretch=1)
        header_layout.addWidget(self.toggle_button)

        # 2. Área de Conteúdo
        self.content_area = content_widget

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.content_area)

        # Conexão de comportamento para recolher/expandir
        self.toggle_button.toggled.connect(self._on_toggle)

    def _update_toggle_icon(self, checked: bool) -> None:
        target_path = self.icon_up_path if checked else self.icon_down_path
        if target_path.exists():
            pixmap = QtGui.QPixmap(str(target_path))
            if not pixmap.isNull():
                self.toggle_button.setIcon(
                    QtGui.QIcon(pixmap.scaled(14, 14, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)))
                return

        # Fallback de segurança caso os SVGs não sejam encontrados
        self.toggle_button.setArrowType(QtCore.Qt.UpArrow if checked else QtCore.Qt.DownArrow)

    def _on_toggle(self, checked: bool) -> None:
        """Alterna o ícone de seta e a visibilidade do conteúdo interno."""
        self.content_area.setVisible(checked)
        self._update_toggle_icon(checked)

    def set_title(self, title: str) -> None:
        """Atualiza o texto do título da seção."""
        self.lbl_title.setText(title)

    def is_expanded(self) -> bool:
        """Retorna se a seção está expandida ou recolhida."""
        return self.toggle_button.isChecked()

    def set_expanded(self, expanded: bool) -> None:
        """Define programaticamente o estado expandido ou recolhido."""
        self.toggle_button.setChecked(expanded)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Teste - CollapsibleSectionTabs")
    window.resize(300, 200)

    content = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout(content)
    lay.addWidget(QtWidgets.QPushButton("Botão Interno 1"))
    lay.addWidget(QtWidgets.QPushButton("Botão Interno 2"))

    section = CollapsibleSectionTabs("Widget 1", content)

    window.setCentralWidget(section)
    window.show()

    sys.exit(app.exec())