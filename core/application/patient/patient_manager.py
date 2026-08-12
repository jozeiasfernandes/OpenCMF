from __future__ import annotations

import time
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6 import QtCore


class PatientManager(QtCore.QObject):
    """Gerenciador centralizado e reativo da sessão do paciente na aplicação (Singleton)."""

    _instance: Optional["PatientManager"] = None

    patient_changed = QtCore.Signal(str)
    patient_data_loaded = QtCore.Signal(dict)

    def __init__(self, project_service=None):
        if PatientManager._instance is not None:
            raise RuntimeError("PatientManager é um Singleton. Use PatientManager.get_instance()")

        super().__init__()
        self.project_service = project_service
        self._current_path: Optional[str] = None
        self._project_data: Dict[str, Any] = {}

        self._last_emitted_path: Optional[str] = None
        self._last_emit_time: float = 0.0

        PatientManager._instance = self

    @classmethod
    def get_instance(cls, project_service=None) -> "PatientManager":
        """Retorna a instância única do PatientManager."""
        if cls._instance is None:
            if project_service is None:
                raise ValueError("ProjectServiceHomePage é obrigatório na primeira inicialização do PatientManager.")
            cls(project_service)
        return cls._instance


    # =========================================================================
    # PROPERTIES
    # =========================================================================
    @property
    def current_path(self) -> Optional[str]:
        """Retorna o caminho absoluto do paciente ativo."""
        return self._current_path

    @property
    def data(self) -> Dict[str, Any]:
        """Retorna o dicionário de dados atual do projeto/paciente."""
        return self._project_data


    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    def set_active_patient(self, path: str):
        """Define o paciente ativo e dispara sinais reativos."""
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

        if self.project_service:
            self._project_data = self.project_service.load_project(Path(resolved_path)) or {}
        else:
            self._project_data = {}

        self.patient_changed.emit(resolved_path)
        self.patient_data_loaded.emit(self._project_data)

    def save_current_data(self):
        """Salva o estado atual dos dados do paciente no disco."""
        if not self._current_path or not self.project_service:
            return

        root = Path(self._current_path)
        self.project_service.save_project(root, self._project_data)

    def clear(self):
        """Limpa a sessão atual do paciente."""
        self._current_path = None
        self._project_data = {}
        self._last_emitted_path = None
        self._last_emit_time = 0.0
        self.patient_changed.emit("")