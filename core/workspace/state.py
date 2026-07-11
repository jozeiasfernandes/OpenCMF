from PySide6 import QtCore
from typing import Dict, Any


class WorkspaceState(QtCore.QObject):
    """
    Fonte central de verdade para o estado da aplicação.
    Implementa o padrão Observer para notificar componentes de mudanças.
    """

    patient_changed = QtCore.Signal(str)
    config_changed = QtCore.Signal(dict)

    def __init__(self):
        super().__init__()
        self._current_patient_path: str = ""
        self._settings: Dict[str, Any] = {}

    @property
    def current_patient(self) -> str:
        return self._current_patient_path

    @current_patient.setter
    def current_patient(self, path: str):
        """Atualiza o paciente e notifica todos os ouvintes."""
        if self._current_patient_path != path:
            self._current_patient_path = path
            self.patient_changed.emit(path)

    def update_settings(self, new_settings: Dict[str, Any]):
        """Atualiza configurações globais e notifica o sistema."""
        self._settings.update(new_settings)
        self.config_changed.emit(self._settings)

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)