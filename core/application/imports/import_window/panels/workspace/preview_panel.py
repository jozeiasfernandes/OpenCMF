from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
import os


class PreviewPanel(QWidget):
    """Painel de Pré-visualização Inferior (PreviewPanel) alinhado ao wireframe."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(12)

        # 1. Coluna de Metadados à esquerda
        meta_layout = QVBoxLayout()
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(4)

        self.title_label = QLabel("<b>Preview:</b> Nenhum item selecionado")
        self.date_label = QLabel("Data de criação: -")
        self.size_label = QLabel("Tamanho: -")

        meta_layout.addWidget(self.title_label)
        meta_layout.addWidget(self.date_label)
        meta_layout.addWidget(self.size_label)
        meta_layout.addStretch()

        main_layout.addLayout(meta_layout, stretch=1)

        # 2. Caixa de Pré-visualização de Imagem à direita (conforme wireframe)
        self.img_preview = QLabel(self)
        self.img_preview.setAlignment(Qt.AlignCenter)
        self.img_preview.setStyleSheet(
            "background-color: #222; color: #aaa; border: 1px solid #444; border-radius: 4px;"
        )
        self.img_preview.setText("[ Pré-visualização da Imagem ]")
        self.img_preview.setFixedSize(180, 120)

        main_layout.addWidget(self.img_preview)

    def update_preview(self, file_path: str):
        """Atualiza o painel de preview com os dados reais do arquivo selecionado."""
        if not file_path or not os.path.exists(file_path):
            self.title_label.setText("<b>Preview:</b> Arquivo inválido")
            self.date_label.setText("Data de criação: -")
            self.size_label.setText("Tamanho: -")
            self.img_preview.setText("[ Indisponível ]")
            return

        file_name = os.path.basename(file_path)
        file_size_bytes = os.path.getsize(file_path)

        # Formatação amigável do tamanho
        if file_size_bytes > 1024 * 1024:
            size_str = f"{file_size_bytes / (1024 * 1024):.2f} mb"
        else:
            size_str = f"{file_size_bytes / 1024:.2f} KB"

        # Data de modificação/criação do arquivo
        import time
        mod_time = time.strftime('%d/%m/%Y', time.localtime(os.path.getmtime(file_path)))

        self.title_label.setText(f"<b>Preview:</b> {file_name}")
        self.date_label.setText(f"Data de criação: {mod_time}")
        self.size_label.setText(f"Tamanho: {size_str}")

        # Se for uma imagem suportada, carrega no preview à direita
        lower_path = file_path.lower()
        if lower_path.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.img_preview.setPixmap(
                    pixmap.scaled(self.img_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                return

        # Fallback caso não seja imagem
        self.img_preview.setText("[ Sem pré-visualização ]")


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    panel = PreviewPanel()
    panel.resize(600, 160)
    panel.show()

    sys.exit(app.exec())