from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui


class CollapsibleSectionFloating(QtWidgets.QWidget):
    """
    Componente retrátil (Accordion/Sanfona) especializado para o Modo Floating.
    Apresenta um puxador de arrasto (drag_indicator.svg), título e botão de alternância (arrow_up/down).
    """

    def __init__(self, title: str, content_widget: QtWidgets.QWidget, parent=None):
        super().__init__(parent)

        # Caminho absoluto para a pasta de ícones (C:\OpenCMF\appearance\icons_manager)
        self.assets_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "appearance" / "icons_manager"

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Layout do Cabeçalho da Seção (Puxador + Título + Botão de Expandir/Recolher)
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(4, 2, 4, 2)
        header_layout.setSpacing(6)

        # Puxador de arrasto (Grip)
        self.btn_grip = QtWidgets.QLabel(self)
        self.btn_grip.setCursor(QtCore.Qt.SizeVerCursor)
        self.btn_grip.setToolTip("Arraste para mover")

        drag_icon_path = self.assets_dir / "drag_indicator.svg"
        if drag_icon_path.exists():
            pixmap_grip = QtGui.QPixmap(str(drag_icon_path))
            if not pixmap_grip.isNull():
                self.btn_grip.setPixmap(
                    pixmap_grip.scaled(16, 16, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                )
            else:
                self.btn_grip.setText("⋮⋮")
                self.btn_grip.setStyleSheet("colors: #888; font-weight: bold; font-size: 11px;")
        else:
            self.btn_grip.setText("⋮⋮")
            self.btn_grip.setStyleSheet("colors: #888; font-weight: bold; font-size: 11px;")

        # Título da Seção
        self.lbl_title = QtWidgets.QLabel(title, self)
        self.lbl_title.setStyleSheet("font-weight: bold;")

        # Botão de Ocultar/Exibir Conteúdo
        self.toggle_button = QtWidgets.QToolButton(self)
        self.toggle_button.setStyleSheet("""
            QToolButton {
                border: none;
                background-colors: transparent;
            }
            QToolButton:hover {
                background-colors: rgba(255, 255, 255, 20);
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

        # 2. Área do Conteúdo Interno
        self.content_area = content_widget

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.content_area)

        # Conexão do evento de clique para alternar visibilidade
        self.toggle_button.toggled.connect(self._on_toggle)

    def _update_toggle_icon(self, checked: bool) -> None:
        """Atualiza o ícone do botão com base no estado expandido/recolhido."""
        target_path = self.icon_up_path if checked else self.icon_down_path
        if target_path.exists():
            pixmap = QtGui.QPixmap(str(target_path))
            if not pixmap.isNull():
                self.toggle_button.setIcon(
                    QtGui.QIcon(pixmap.scaled(14, 14, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                )
                return

        self.toggle_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarShadeButton))

    def _on_toggle(self, checked: bool) -> None:
        """Alterna a visibilidade do conteúdo e atualiza a seta."""
        self.content_area.setVisible(checked)
        self._update_toggle_icon(checked)

    def set_title(self, title: str) -> None:
        """Atualiza o texto do título da seção."""
        self.lbl_title.setText(title)

    def is_expanded(self) -> bool:
        """Retorna True se a seção estiver expandida."""
        return self.toggle_button.isChecked()

    def set_expanded(self, expanded: bool) -> None:
        """Define o estado de expansão da seção."""
        self.toggle_button.setChecked(expanded)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Teste - CollapsibleSectionFloating")
    window.resize(300, 200)

    content = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout(content)
    lay.addWidget(QtWidgets.QPushButton("Ferramenta Flutuante 1"))
    lay.addWidget(QtWidgets.QPushButton("Ferramenta Flutuante 2"))

    section = CollapsibleSectionFloating("Floating Widget 1", content)

    window.setCentralWidget(section)
    window.show()

    sys.exit(app.exec())