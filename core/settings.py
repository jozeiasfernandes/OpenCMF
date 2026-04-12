# core/settings.py

import json
import logging
from pathlib import Path
from typing import Any, Dict

class SettingsManager:
    def __init__(self, file_name: str = "config.json"):
        self.path = Path(__file__).parent.parent / file_name
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
                "titulo": "OpenCMF - Modular Surgical Planning",
                "version": "1.0.0"
            },
            "preferencias": {
                "tema": "dark",
                "idioma": "pt_BR",
                "autosave": True
            },
            "diretorios": {
                "pacientes": "pacientes",
                "fluxos": "fluxos",
                "icones": "icones"
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

settings = SettingsManager()