from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.settings.paths.list_paths import FLOWS_DIR


class FlowService:
    def __init__(self, flows_dir: Optional[Path] = None):
        self.flows_dir = Path(flows_dir) if flows_dir else FLOWS_DIR
        self._ensure_base_directory()

    def _ensure_base_directory(self) -> None:
        self.flows_dir.mkdir(parents=True, exist_ok=True)

    def load_flow(self, flow_path: Path) -> Optional[Dict[str, Any]]:
        return self._load_json(flow_path)

    def list_flows(self, exclude_file: Optional[str] = None) -> List[Dict[str, Any]]:
        flows = []

        for file_path in self.flows_dir.glob("*.json"):
            if exclude_file and file_path.name == Path(exclude_file).name:
                continue

            data = self._load_json(file_path)
            if not data:
                continue

            data["_file_path"] = str(file_path)
            flows.append(data)

        return flows

    def save_flow(self, file_name: str, data: Dict[str, Any]) -> Path:
        try:
            file_path = self.flows_dir / file_name

            if not file_path.suffix == ".json":
                file_path = file_path.with_suffix(".json")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            return file_path

        except Exception as e:
            logging.error(f"Failed to save flow {file_name}: {e}")
            raise

    def delete_flow(self, flow_path: str) -> bool:
        try:
            path = Path(flow_path)

            if path.is_file():
                path.unlink()
                return True

            return False

        except Exception as e:
            logging.error(f"Failed to delete flow {flow_path}: {e}")
            return False

    def get_flow_names(self) -> List[str]:
        return [f.stem for f in self.flows_dir.glob("*.json")]

    def flow_exists(self, name: str) -> bool:
        return (self.flows_dir / f"{name}.json").exists()

    def _load_json(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            if not path.exists():
                return None

            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to load JSON at {path}: {e}")
            return None