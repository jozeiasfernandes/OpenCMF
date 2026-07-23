from typing import Any, Dict

from PySide6 import QtCore


class WorkspaceState(QtCore.QObject):

    patient_changed = QtCore.Signal(str)
    config_changed = QtCore.Signal(dict)
    setting_changed = QtCore.Signal(str, object)

    def __init__(self) -> None:
        super().__init__()
        self._current_patient_path: str = ""
        self._settings: Dict[str, Any] = {}

    @property
    def current_patient(self) -> str:
        return self._current_patient_path

    @current_patient.setter
    def current_patient(self, path: str) -> None:
        normalized_path = str(path) if path else ""
        if self._current_patient_path != normalized_path:
            self._current_patient_path = normalized_path
            self.patient_changed.emit(normalized_path)

    def update_setting(self, key: str, value: Any) -> None:
        if self._settings.get(key) != value:
            self._settings[key] = value
            self.setting_changed.emit(key, value)
            self.config_changed.emit(self._settings.copy())

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def get_all_settings(self) -> Dict[str, Any]:
        return self._settings.copy()