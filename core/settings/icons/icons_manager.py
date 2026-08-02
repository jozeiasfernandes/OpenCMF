import json
import logging
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QSize, Qt
from PySide6.QtSvg import QSvgRenderer

from list_paths import ICONS_DIR, ICONS_THEMES_DIR


class IconManager:
    _instance = None

    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else ICONS_DIR
        self._cache = {}

    @classmethod
    def set_base_path(cls, path=None):
        cls._instance = IconManager(path)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = IconManager(ICONS_DIR)
        return cls._instance

    def get_color(self, theme_name: str, group: str, state: str = "default") -> str:
        json_path = ICONS_THEMES_DIR / f"{theme_name}.json"

        try:
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("icons", {}).get(group, {}).get(state, "#FFFFFF")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Erro ao ler tema {theme_name}: {e}")

        return "#FFFFFF"

    def get_icon(self, icon_name, color=None, size=24):
        cache_key = f"{icon_name}_{color}_{size}"
        if cache_key not in self._cache:
            file_path = self.base_path / f"{icon_name}.svg"
            if not file_path.exists():
                logging.warning(f"Ícone não encontrado: {file_path}")
                return QIcon()

            self._cache[cache_key] = self._create_colored_icon(str(file_path), color, size) if color else QIcon(
                str(file_path))
        return self._cache[cache_key]

    def _create_colored_icon(self, file_path, color_hex, size):
        renderer = QSvgRenderer(file_path)
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter, pixmap.rect())

        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color_hex))
        painter.end()

        return QIcon(pixmap)