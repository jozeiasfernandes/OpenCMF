from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6 import QtCore


class PatientManager(QtCore.QObject):
    """Gerenciador de sessão reativo do paciente (Injetado, sem Singleton)."""

    patient_changed = QtCore.Signal(str)
    patient_data_loaded = QtCore.Signal(dict)

    def __init__(self, config_manager: Any = None) -> None:
        super().__init__()
        self.config_manager = config_manager

        self._current_path: Optional[str] = None
        self._project_data: Dict[str, Any] = {}

        self._last_emitted_path: Optional[str] = None
        self._last_emit_time: float = 0.0

    # =========================================================================
    # PROPERTIES
    # =========================================================================
    @property
    def current_path(self) -> Optional[str]:
        return self._current_path

    @property
    def data(self) -> Dict[str, Any]:
        return self._project_data

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    def set_active_patient(self, path: str | Path) -> None:
        if not path:
            return

        resolved_path = str(Path(path).resolve())
        current_time = time.time()

        if self._current_path == resolved_path and resolved_path == self._last_emitted_path:
            if (current_time - self._last_emit_time) < 0.4:
                return

        self._current_path = resolved_path
        self._last_emitted_path = resolved_path
        self._last_emit_time = current_time

        if self.config_manager and hasattr(self.config_manager, "load_patient_record"):
            loaded_data = self.config_manager.load_patient_record(Path(resolved_path))
            self._project_data = loaded_data if loaded_data is not None else {}
        else:
            record_path = Path(resolved_path) / "project" / "patient_record.json"
            if record_path.exists():
                try:
                    self._project_data = json.loads(record_path.read_text(encoding="utf-8"))
                except Exception:
                    self._project_data = {}
            else:
                self._project_data = {}

        self.patient_changed.emit(resolved_path)
        self.patient_data_loaded.emit(self._project_data)

    def save_current_data(self) -> None:
        if not self._current_path or not self.config_manager:
            return

        if hasattr(self.config_manager, "save_patient_record"):
            root = Path(self._current_path)
            self.config_manager.save_patient_record(root, self._project_data)

    def clear(self) -> None:
        self._current_path = None
        self._project_data = {}
        self._last_emitted_path = None
        self._last_emit_time = 0.0
        self.patient_changed.emit("")
        self.patient_data_loaded.emit({})