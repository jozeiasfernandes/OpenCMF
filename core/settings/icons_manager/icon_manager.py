import json
import logging
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

from core.settings.paths.list_paths import ICONS_DIR, ICONS_DIR


class IconManager:
    _instance = None

    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else ICONS_DIR
        self._cache = {}
        self._themes_cache = {}  # Cache para evitar leitura repetida de JSONs

    @classmethod
    def set_base_path(cls, path=None):
        cls._instance = IconManager(path)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = IconManager(ICONS_DIR)
        return cls._instance

    def clear_cache(self):
        """Limpa o cache de ícones renderizados e de temas carregados."""
        self._cache.clear()
        self._themes_cache.clear()

    def _load_theme(self, theme_name: str) -> dict:
        if theme_name in self._themes_cache:
            return self._themes_cache[theme_name]

        json_path = ICONS_DIR / f"{theme_name}.json"
        data = {}
        try:
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Erro ao ler tema {theme_name}: {e}")

        self._themes_cache[theme_name] = data
        return data

    def get_color(self, theme_name: str, group: str, state: str = "default") -> str:
        theme_data = self._load_theme(theme_name)
        return theme_data.get("icons_manager", {}).get(group, {}).get(state, "#FFFFFF")

    def get_icon(self, icon_name, color=None, size=24):
        cache_key = f"{icon_name}_{color}_{size}"
        if cache_key not in self._cache:
            file_path = self.base_path / f"{icon_name}.svg"
            if not file_path.exists():
                logging.warning(f"Ícone não encontrado: {file_path}")
                return QIcon()

            if color:
                self._cache[cache_key] = self._create_colored_icon(str(file_path), color, size)
            else:
                self._cache[cache_key] = QIcon(str(file_path))

        return self._cache[cache_key]

    def get_app_icon(self, size=24) -> QIcon:
        """Calcula automaticamente a cor ideal com base na paleta atual e retorna o ícone da aplicação."""
        window_bg_color = QApplication.palette().color(QPalette.ColorRole.Window)
        luminance = (0.299 * window_bg_color.red() +
                     0.587 * window_bg_color.green() +
                     0.114 * window_bg_color.blue())

        color = "#FFFFFF" if luminance < 128 else "#333333"
        return self.get_icon("cmf", color=color, size=size)

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