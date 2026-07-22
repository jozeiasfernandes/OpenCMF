import json
import logging
from pathlib import Path
from typing import Any, Dict


class SettingsManager:
    def __init__(self, file_name: str = "config.json"):
        self.path = Path(__file__).parent / file_name
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Failed to parse settings: {e}")
                self._apply_defaults()
        else:
            self._apply_defaults()
            self.save()

    def _apply_defaults(self) -> None:
        self.data = {
            "app_info": {
                "id": "opencmf.surgicalplanning.1.0",
                "title": "OpenCMF - Modular Surgical Planning",
                "version": "1.0.0"
            },
            "preferencias": {
                "tema": "dark",
                "idioma": "pt_BR",
                "autosave": True
            },
            "diretorios": {
                "patients": "patients",
                "flows": "flows",
                "icons": "icons"
            },
            "side_panel": {
                "show_by_default": True,
                "width": 250,
                "mode": "tabs"
            }
        }

    def get(self, category: str, key: str, default: Any = None) -> Any:
        return self.data.get(category, {}).get(key, default)

    def set(self, category: str, key: str, value: Any) -> None:
        if category not in self.data:
            self.data[category] = {}
        self.data[category][key] = value

    def save(self) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Failed to save settings: {e}")

    @property
    def tema(self) -> str:
        return self.get("preferencias", "tema", "dark")

    @tema.setter
    def tema(self, value: str):
        self.set("preferencias", "tema", value)
        self.save()

    @property
    def side_panel_show_by_default(self) -> bool:
        return self.get("side_panel", "show_by_default", True)

    @side_panel_show_by_default.setter
    def side_panel_show_by_default(self, value: bool):
        self.set("side_panel", "show_by_default", value)
        self.save()

    @property
    def side_panel_width(self) -> int:
        return self.get("side_panel", "width", 250)

    @side_panel_width.setter
    def side_panel_width(self, value: int):
        self.set("side_panel", "width", value)
        self.save()

    @property
    def side_panel_mode(self) -> str:
        return self.get("side_panel", "mode", "tabs")

    @side_panel_mode.setter
    def side_panel_mode(self, value: str):
        self.set("side_panel", "mode", value)
        self.save()


settings = SettingsManager()