from typing import Dict, Any, Optional
from PySide6 import QtCore

class WorkspaceState(QtCore.QObject):
    """
    Fonte central de verdade para o estado da aplicação.
    Implementa o padrão Observer para notificar componentes de mudanças.
    """

    patient_changed = QtCore.Signal(str)
    # Notificação genérica para configurações gerais
    config_changed = QtCore.Signal(dict)
    # Notificação granular (ex: "tema_changed", "idioma_changed")
    setting_changed = QtCore.Signal(str, object)

    def __init__(self):
        super().__init__()
        self._current_patient_path: str = ""
        self._settings: Dict[str, Any] = {}

    @property
    def current_patient(self) -> str:
        return self._current_patient_path

    @current_patient.setter
    def current_patient(self, path: str):
        if self._current_patient_path != path:
            self._current_patient_path = path
            self.patient_changed.emit(path)

    def update_setting(self, key: str, value: Any):
        """Atualiza uma única configuração e notifica especificamente."""
        if self._settings.get(key) != value:
            self._settings[key] = value
            # Notifica ouvintes específicos da chave e ouvintes globais
            self.setting_changed.emit(key, value)
            self.config_changed.emit(self._settings)

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)