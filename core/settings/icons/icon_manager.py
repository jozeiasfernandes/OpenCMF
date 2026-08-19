from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

from core.settings.paths.list_paths import ICONS_DIR
from core.settings.icons.theme_color_manager import ThemeColorManager  # Ajuste o import se necessário

logger = logging.getLogger(f"OpenCMF.Core.{__name__.split('.')[-1]}")


class IconManager:
    """Gerenciador centralizado para carregamento, coloração dinâmica e cache de ícones SVG."""

    _instance: Optional[IconManager] = None

    def __init__(self, base_path: Optional[Path | str] = None) -> None:
        self.base_path = Path(base_path) if base_path else ICONS_DIR
        self._cache: Dict[str, QIcon] = {}

    @classmethod
    def set_base_path(cls, path: Optional[Path | str] = None) -> None:
        cls._instance = IconManager(path)

    @classmethod
    def get_instance(cls) -> IconManager:
        if cls._instance is None:
            cls._instance = IconManager(ICONS_DIR)
        return cls._instance

    def clear_cache(self) -> None:
        """Limpa o cache de ícones renderizados e também o cache de cores dos temas."""
        self._cache.clear()
        ThemeColorManager.get_instance().clear_cache()

    def get_color(self, theme_name: str, group: str, state: str = "default") -> str:
        """Delega a busca de cores para o ThemeColorManager para manter compatibilidade."""
        return ThemeColorManager.get_instance().get_color(theme_name, group, state)

    def get_icon(self, icon_name: str, color: Optional[str] = None, size: int = 24) -> QIcon:
        """Retorna o ícone solicitado, aplicando coloração personalizada e cache sob demanda."""
        cache_key = f"{icon_name}_{color}_{size}"

        if cache_key not in self._cache:
            file_path = self.base_path / f"{icon_name}.svg"
            if not file_path.exists():
                logger.warning(f"Ícone não encontrado no caminho: {file_path}")
                return QIcon()

            if color:
                self._cache[cache_key] = self._create_colored_icon(file_path, color, size)
            else:
                self._cache[cache_key] = QIcon(str(file_path))

        return self._cache[cache_key]

    def get_app_icon(self, size: int = 24) -> QIcon:
        """Calcula automaticamente a cor ideal com base na paleta atual e retorna o ícone da aplicação."""
        window_bg_color = QApplication.palette().color(QPalette.ColorRole.Window)

        luminance = (0.299 * window_bg_color.red() +
                     0.587 * window_bg_color.green() +
                     0.114 * window_bg_color.blue())

        color = "#FFFFFF" if luminance < 128 else "#333333"
        return self.get_icon("cmf", color=color, size=size)

    def _create_colored_icon(self, file_path: Path, color_hex: str, size: int) -> QIcon:
        renderer = QSvgRenderer(str(file_path))

        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter, pixmap.rect())

        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color_hex))
        painter.end()

        return QIcon(pixmap)